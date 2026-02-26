from flask import (
    Blueprint, render_template, session, redirect, url_for, request, jsonify,
    g, abort,
)
from ..models import db, Category, MenuItem, Restaurant

public_bp = Blueprint("public", __name__)


# ── helpers ──────────────────────────────────────────────────────────────────
def _load_restaurant(slug):
    restaurant = Restaurant.query.filter_by(slug=slug).first_or_404()
    g.restaurant = restaurant
    return restaurant


def _get_picks() -> list[int]:
    return session.get("picks", [])


def _set_picks(picks: list[int]):
    session["picks"] = picks


# ── directory (root) ────────────────────────────────────────────────────────
@public_bp.route("/")
def directory():
    restaurants = Restaurant.query.order_by(Restaurant.name).all()
    return render_template("public/directory.html", restaurants=restaurants)


# ── landing page ─────────────────────────────────────────────────────────────
@public_bp.route("/<slug>/")
def landing(slug):
    _load_restaurant(slug)
    return render_template("public/landing.html")


# ── menu listing ─────────────────────────────────────────────────────────────
@public_bp.route("/<slug>/menu/<menu_type>")
def menu(slug, menu_type):
    restaurant = _load_restaurant(slug)
    if menu_type not in ("dining", "beverages"):
        return redirect(url_for("public.landing", slug=slug))
    categories = (
        Category.query
        .filter_by(restaurant_id=restaurant.id, menu_type=menu_type)
        .order_by(Category.sort_order)
        .all()
    )
    return render_template(
        "public/menu.html",
        categories=categories,
        menu_type=menu_type,
        picks=_get_picks(),
    )


# ── category page ────────────────────────────────────────────────────────────
@public_bp.route("/<slug>/category/<int:category_id>")
def category(slug, category_id):
    restaurant = _load_restaurant(slug)
    cat = db.get_or_404(Category, category_id)
    if cat.restaurant_id != restaurant.id:
        abort(404)
    items = (
        MenuItem.query
        .filter_by(category_id=cat.id, available=True)
        .order_by(MenuItem.sort_order)
        .all()
    )
    return render_template(
        "public/category.html", category=cat, items=items, picks=_get_picks(),
    )


# ── item detail ──────────────────────────────────────────────────────────────
@public_bp.route("/<slug>/item/<int:item_id>")
def item_detail(slug, item_id):
    restaurant = _load_restaurant(slug)
    item = db.get_or_404(MenuItem, item_id)
    if item.category.restaurant_id != restaurant.id:
        abort(404)
    return render_template(
        "public/item_detail.html", item=item, picks=_get_picks(),
    )


# ── search ───────────────────────────────────────────────────────────────────
@public_bp.route("/<slug>/search")
def search(slug):
    restaurant = _load_restaurant(slug)
    q = request.args.get("q", "").strip()
    results = []
    if q:
        results = (
            MenuItem.query
            .join(Category)
            .filter(Category.restaurant_id == restaurant.id)
            .filter(MenuItem.available.is_(True))
            .filter(MenuItem.name.ilike(f"%{q}%"))
            .order_by(MenuItem.name)
            .limit(50)
            .all()
        )
    return render_template("public/search.html", query=q, results=results, picks=_get_picks())


# ── shortlist ("My Picks") ──────────────────────────────────────────────────
@public_bp.route("/<slug>/picks")
def picks(slug):
    _load_restaurant(slug)
    pick_ids = _get_picks()
    items = MenuItem.query.filter(MenuItem.id.in_(pick_ids)).all() if pick_ids else []
    # Group by category, preserve order
    by_cat: dict[str, list[MenuItem]] = {}
    for item in items:
        by_cat.setdefault(item.category.name, []).append(item)
    return render_template("public/picks.html", by_category=by_cat, picks=pick_ids)


@public_bp.route("/<slug>/picks/add/<int:item_id>", methods=["POST"])
def pick_add(slug, item_id):
    _load_restaurant(slug)
    item = db.get_or_404(MenuItem, item_id)
    picks = _get_picks()
    if item.id not in picks:
        picks.append(item.id)
        _set_picks(picks)
    # Return JSON for fetch() calls, redirect for plain form posts
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(ok=True, count=len(picks))
    return redirect(request.referrer or url_for("public.landing", slug=slug))


@public_bp.route("/<slug>/picks/remove/<int:item_id>", methods=["POST"])
def pick_remove(slug, item_id):
    _load_restaurant(slug)
    picks = _get_picks()
    if item_id in picks:
        picks.remove(item_id)
        _set_picks(picks)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(ok=True, count=len(picks))
    return redirect(request.referrer or url_for("public.picks", slug=slug))


@public_bp.route("/<slug>/picks/clear", methods=["POST"])
def picks_clear(slug):
    _load_restaurant(slug)
    _set_picks([])
    return redirect(url_for("public.picks", slug=slug))
