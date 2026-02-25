from flask import (
    Blueprint, render_template, session, redirect, url_for, request, jsonify,
)
from ..models import db, Category, MenuItem

public_bp = Blueprint("public", __name__, template_folder="../templates/public")


# ── helpers ──────────────────────────────────────────────────────────────────
def _get_picks() -> list[int]:
    return session.get("picks", [])


def _set_picks(picks: list[int]):
    session["picks"] = picks


# ── landing page ─────────────────────────────────────────────────────────────
@public_bp.route("/")
def landing():
    return render_template("landing.html")


# ── menu listing ─────────────────────────────────────────────────────────────
@public_bp.route("/menu/<menu_type>")
def menu(menu_type):
    if menu_type not in ("dining", "beverages"):
        return redirect(url_for("public.landing"))
    categories = (
        Category.query
        .filter_by(menu_type=menu_type)
        .order_by(Category.sort_order)
        .all()
    )
    return render_template(
        "menu.html",
        categories=categories,
        menu_type=menu_type,
        picks=_get_picks(),
    )


# ── category page ────────────────────────────────────────────────────────────
@public_bp.route("/category/<int:category_id>")
def category(category_id):
    cat = db.get_or_404(Category, category_id)
    items = (
        MenuItem.query
        .filter_by(category_id=cat.id, available=True)
        .order_by(MenuItem.sort_order)
        .all()
    )
    return render_template(
        "category.html", category=cat, items=items, picks=_get_picks(),
    )


# ── item detail ──────────────────────────────────────────────────────────────
@public_bp.route("/item/<int:item_id>")
def item_detail(item_id):
    item = db.get_or_404(MenuItem, item_id)
    return render_template(
        "item_detail.html", item=item, picks=_get_picks(),
    )


# ── search ───────────────────────────────────────────────────────────────────
@public_bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        results = (
            MenuItem.query
            .filter(MenuItem.available.is_(True))
            .filter(MenuItem.name.ilike(f"%{q}%"))
            .order_by(MenuItem.name)
            .limit(50)
            .all()
        )
    return render_template("search.html", query=q, results=results, picks=_get_picks())


# ── shortlist ("My Picks") ──────────────────────────────────────────────────
@public_bp.route("/picks")
def picks():
    pick_ids = _get_picks()
    items = MenuItem.query.filter(MenuItem.id.in_(pick_ids)).all() if pick_ids else []
    # Group by category, preserve order
    by_cat: dict[str, list[MenuItem]] = {}
    for item in items:
        by_cat.setdefault(item.category.name, []).append(item)
    return render_template("picks.html", by_category=by_cat, picks=pick_ids)


@public_bp.route("/picks/add/<int:item_id>", methods=["POST"])
def pick_add(item_id):
    item = db.get_or_404(MenuItem, item_id)
    picks = _get_picks()
    if item.id not in picks:
        picks.append(item.id)
        _set_picks(picks)
    # Return JSON for fetch() calls, redirect for plain form posts
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(ok=True, count=len(picks))
    return redirect(request.referrer or url_for("public.landing"))


@public_bp.route("/picks/remove/<int:item_id>", methods=["POST"])
def pick_remove(item_id):
    picks = _get_picks()
    if item_id in picks:
        picks.remove(item_id)
        _set_picks(picks)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(ok=True, count=len(picks))
    return redirect(request.referrer or url_for("public.picks"))


@public_bp.route("/picks/clear", methods=["POST"])
def picks_clear():
    _set_picks([])
    return redirect(url_for("public.picks"))
