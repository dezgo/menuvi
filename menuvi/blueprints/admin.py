import functools

from flask import (
    Blueprint, render_template, request, redirect, url_for, session, flash,
    current_app,
)
from ..models import db, Category, MenuItem

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


# ── auth ─────────────────────────────────────────────────────────────────────
def admin_required(view):
    @functools.wraps(view)
    def wrapped(**kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin.login", next=request.url))
        return view(**kwargs)
    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pw = request.form.get("password", "")
        if pw == current_app.config["ADMIN_PASSWORD"]:
            session["admin"] = True
            dest = request.args.get("next") or url_for("admin.dashboard")
            return redirect(dest)
        flash("Incorrect password.", "error")
    return render_template("login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("public.landing"))


# ── dashboard ────────────────────────────────────────────────────────────────
@admin_bp.route("/")
@admin_required
def dashboard():
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template("dashboard.html", categories=categories)


# ── category CRUD ────────────────────────────────────────────────────────────
@admin_bp.route("/category/new", methods=["GET", "POST"])
@admin_required
def category_new():
    if request.method == "POST":
        name = request.form["name"].strip()
        menu_type = request.form.get("menu_type", "dining")
        sort_order = int(request.form.get("sort_order", 0))
        if not name:
            flash("Name is required.", "error")
            return render_template("category_form.html", cat=None)
        cat = Category(name=name, menu_type=menu_type, sort_order=sort_order)
        db.session.add(cat)
        db.session.commit()
        flash(f"Category '{name}' created.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("category_form.html", cat=None)


@admin_bp.route("/category/<int:cat_id>/edit", methods=["GET", "POST"])
@admin_required
def category_edit(cat_id):
    cat = db.get_or_404(Category, cat_id)
    if request.method == "POST":
        cat.name = request.form["name"].strip()
        cat.menu_type = request.form.get("menu_type", cat.menu_type)
        cat.sort_order = int(request.form.get("sort_order", cat.sort_order))
        db.session.commit()
        flash(f"Category '{cat.name}' updated.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("category_form.html", cat=cat)


@admin_bp.route("/category/<int:cat_id>/delete", methods=["POST"])
@admin_required
def category_delete(cat_id):
    cat = db.get_or_404(Category, cat_id)
    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f"Category '{name}' and all its items deleted.", "success")
    return redirect(url_for("admin.dashboard"))


# ── item CRUD ────────────────────────────────────────────────────────────────
@admin_bp.route("/category/<int:cat_id>/items")
@admin_required
def item_list(cat_id):
    cat = db.get_or_404(Category, cat_id)
    items = MenuItem.query.filter_by(category_id=cat.id).order_by(MenuItem.sort_order).all()
    return render_template("item_list.html", category=cat, items=items)


@admin_bp.route("/category/<int:cat_id>/item/new", methods=["GET", "POST"])
@admin_required
def item_new(cat_id):
    cat = db.get_or_404(Category, cat_id)
    if request.method == "POST":
        name = request.form["name"].strip()
        desc = request.form.get("description", "").strip()
        price_str = request.form.get("price", "").strip()
        sort_order = int(request.form.get("sort_order", 0))
        available = "available" in request.form

        price_cents = _parse_price(price_str)

        if not name:
            flash("Name is required.", "error")
            return render_template("item_form.html", category=cat, item=None)

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
        return redirect(url_for("admin.item_list", cat_id=cat.id))
    return render_template("item_form.html", category=cat, item=None)


@admin_bp.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
@admin_required
def item_edit(item_id):
    item = db.get_or_404(MenuItem, item_id)
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
        return redirect(url_for("admin.item_list", cat_id=item.category_id))
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template("item_form.html", category=cat, item=item, categories=categories)


@admin_bp.route("/item/<int:item_id>/delete", methods=["POST"])
@admin_required
def item_delete(item_id):
    item = db.get_or_404(MenuItem, item_id)
    cat_id = item.category_id
    name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f"Item '{name}' deleted.", "success")
    return redirect(url_for("admin.item_list", cat_id=cat_id))


@admin_bp.route("/item/<int:item_id>/toggle", methods=["POST"])
@admin_required
def item_toggle(item_id):
    item = db.get_or_404(MenuItem, item_id)
    item.available = not item.available
    db.session.commit()
    status = "available" if item.available else "unavailable"
    flash(f"'{item.name}' marked as {status}.", "success")
    return redirect(url_for("admin.item_list", cat_id=item.category_id))


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
