import functools
import io

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    send_file, g, abort,
)
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db, Category, MenuItem, Restaurant, User

admin_bp = Blueprint("admin", __name__)


# ── helpers ─────────────────────────────────────────────────────────────────
def _load_restaurant(slug):
    restaurant = Restaurant.query.filter_by(slug=slug).first_or_404()
    g.restaurant = restaurant
    return restaurant


def admin_required(view):
    @functools.wraps(view)
    @login_required
    def wrapped(slug, **kwargs):
        restaurant = _load_restaurant(slug)
        # User must own this restaurant or be superadmin
        if not current_user.is_superadmin and current_user.restaurant_id != restaurant.id:
            abort(403)
        return view(slug=slug, **kwargs)
    return wrapped


# ── auth ─────────────────────────────────────────────────────────────────────
@admin_bp.route("/<slug>/admin/login", methods=["GET", "POST"])
def login(slug):
    restaurant = _load_restaurant(slug)
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        pw = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(pw):
            # Must belong to this restaurant or be superadmin
            if user.is_superadmin or user.restaurant_id == restaurant.id:
                login_user(user)
                dest = request.args.get("next") or url_for("admin.dashboard", slug=slug)
                return redirect(dest)
        flash("Invalid email or password.", "error")
    return render_template("admin/login.html")


@admin_bp.route("/<slug>/admin/logout")
def logout(slug):
    logout_user()
    return redirect(url_for("public.landing", slug=slug))


# ── dashboard ────────────────────────────────────────────────────────────────
@admin_bp.route("/<slug>/admin/")
@admin_required
def dashboard(slug):
    categories = (
        Category.query
        .filter_by(restaurant_id=g.restaurant.id)
        .order_by(Category.sort_order)
        .all()
    )
    return render_template("admin/dashboard.html", categories=categories)


# ── category CRUD ────────────────────────────────────────────────────────────
@admin_bp.route("/<slug>/admin/category/new", methods=["GET", "POST"])
@admin_required
def category_new(slug):
    if request.method == "POST":
        name = request.form["name"].strip()
        menu_type = request.form.get("menu_type", "dining")
        sort_order = int(request.form.get("sort_order", 0))
        if not name:
            flash("Name is required.", "error")
            return render_template("admin/category_form.html", cat=None)
        cat = Category(
            restaurant_id=g.restaurant.id,
            name=name,
            menu_type=menu_type,
            sort_order=sort_order,
        )
        db.session.add(cat)
        db.session.commit()
        flash(f"Category '{name}' created.", "success")
        return redirect(url_for("admin.dashboard", slug=slug))
    return render_template("admin/category_form.html", cat=None)


@admin_bp.route("/<slug>/admin/category/<int:cat_id>/edit", methods=["GET", "POST"])
@admin_required
def category_edit(slug, cat_id):
    cat = db.get_or_404(Category, cat_id)
    if cat.restaurant_id != g.restaurant.id:
        abort(404)
    if request.method == "POST":
        cat.name = request.form["name"].strip()
        cat.menu_type = request.form.get("menu_type", cat.menu_type)
        cat.sort_order = int(request.form.get("sort_order", cat.sort_order))
        db.session.commit()
        flash(f"Category '{cat.name}' updated.", "success")
        return redirect(url_for("admin.dashboard", slug=slug))
    return render_template("admin/category_form.html", cat=cat)


@admin_bp.route("/<slug>/admin/category/<int:cat_id>/delete", methods=["POST"])
@admin_required
def category_delete(slug, cat_id):
    cat = db.get_or_404(Category, cat_id)
    if cat.restaurant_id != g.restaurant.id:
        abort(404)
    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f"Category '{name}' and all its items deleted.", "success")
    return redirect(url_for("admin.dashboard", slug=slug))


# ── item CRUD ────────────────────────────────────────────────────────────────
@admin_bp.route("/<slug>/admin/category/<int:cat_id>/items")
@admin_required
def item_list(slug, cat_id):
    cat = db.get_or_404(Category, cat_id)
    if cat.restaurant_id != g.restaurant.id:
        abort(404)
    items = MenuItem.query.filter_by(category_id=cat.id).order_by(MenuItem.sort_order).all()
    return render_template("admin/item_list.html", category=cat, items=items)


@admin_bp.route("/<slug>/admin/category/<int:cat_id>/item/new", methods=["GET", "POST"])
@admin_required
def item_new(slug, cat_id):
    cat = db.get_or_404(Category, cat_id)
    if cat.restaurant_id != g.restaurant.id:
        abort(404)
    if request.method == "POST":
        name = request.form["name"].strip()
        desc = request.form.get("description", "").strip()
        price_str = request.form.get("price", "").strip()
        sort_order = int(request.form.get("sort_order", 0))
        available = "available" in request.form

        price_cents = _parse_price(price_str)

        if not name:
            flash("Name is required.", "error")
            return render_template("admin/item_form.html", category=cat, item=None)

        item = MenuItem(
            category_id=cat.id,
            name=name,
            description=desc,
            price_cents=price_cents,
            sort_order=sort_order,
            available=available,
        )
        db.session.add(item)
        db.session.commit()
        flash(f"Item '{name}' created.", "success")
        return redirect(url_for("admin.item_list", slug=slug, cat_id=cat.id))
    return render_template("admin/item_form.html", category=cat, item=None)


@admin_bp.route("/<slug>/admin/item/<int:item_id>/edit", methods=["GET", "POST"])
@admin_required
def item_edit(slug, item_id):
    item = db.get_or_404(MenuItem, item_id)
    if item.category.restaurant_id != g.restaurant.id:
        abort(404)
    cat = item.category
    if request.method == "POST":
        item.name = request.form["name"].strip()
        item.description = request.form.get("description", "").strip()
        item.price_cents = _parse_price(request.form.get("price", ""))
        item.sort_order = int(request.form.get("sort_order", item.sort_order))
        item.available = "available" in request.form
        item.category_id = int(request.form.get("category_id", item.category_id))
        db.session.commit()
        flash(f"Item '{item.name}' updated.", "success")
        return redirect(url_for("admin.item_list", slug=slug, cat_id=item.category_id))
    categories = (
        Category.query
        .filter_by(restaurant_id=g.restaurant.id)
        .order_by(Category.sort_order)
        .all()
    )
    return render_template("admin/item_form.html", category=cat, item=item, categories=categories)


@admin_bp.route("/<slug>/admin/item/<int:item_id>/delete", methods=["POST"])
@admin_required
def item_delete(slug, item_id):
    item = db.get_or_404(MenuItem, item_id)
    if item.category.restaurant_id != g.restaurant.id:
        abort(404)
    cat_id = item.category_id
    name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f"Item '{name}' deleted.", "success")
    return redirect(url_for("admin.item_list", slug=slug, cat_id=cat_id))


@admin_bp.route("/<slug>/admin/item/<int:item_id>/toggle", methods=["POST"])
@admin_required
def item_toggle(slug, item_id):
    item = db.get_or_404(MenuItem, item_id)
    if item.category.restaurant_id != g.restaurant.id:
        abort(404)
    item.available = not item.available
    db.session.commit()
    status = "available" if item.available else "unavailable"
    flash(f"'{item.name}' marked as {status}.", "success")
    return redirect(url_for("admin.item_list", slug=slug, cat_id=item.category_id))


# ── QR code ──────────────────────────────────────────────────────────────────
@admin_bp.route("/<slug>/admin/qr")
@admin_required
def qr_code(slug):
    site_url = request.url_root.rstrip("/") + url_for("public.landing", slug=slug)
    return render_template("admin/qr.html", site_url=site_url)


@admin_bp.route("/<slug>/admin/qr/download")
@admin_required
def qr_download(slug):
    import qrcode

    site_url = request.url_root.rstrip("/") + url_for("public.landing", slug=slug)
    qr = qrcode.QRCode(box_size=20, border=2)
    qr.add_data(site_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png", download_name=f"{slug}-qr.png")


# ── helpers ──────────────────────────────────────────────────────────────────
def _parse_price(s: str) -> int | None:
    """Convert a price string like '22.90' or '$22.90' to cents."""
    if not s:
        return None
    s = s.replace("$", "").replace(",", "").strip()
    try:
        return int(round(float(s) * 100))
    except ValueError:
        return None
