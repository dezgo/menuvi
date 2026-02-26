import functools
import re

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
)
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db, Restaurant, User

superadmin_bp = Blueprint(
    "superadmin", __name__, template_folder="../templates/superadmin",
)


# ── auth helpers ─────────────────────────────────────────────────────────────
def superadmin_required(view):
    @functools.wraps(view)
    @login_required
    def wrapped(**kwargs):
        if not current_user.is_superadmin:
            flash("Superadmin access required.", "error")
            return redirect(url_for("public.directory"))
        return view(**kwargs)
    return wrapped


# ── superadmin login (standalone, not scoped to a restaurant) ───────────────
@superadmin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        pw = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(pw) and user.is_superadmin:
            login_user(user)
            return redirect(url_for("superadmin.dashboard"))
        flash("Invalid credentials or insufficient permissions.", "error")
    return render_template("login.html")


@superadmin_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.directory"))


# ── dashboard ────────────────────────────────────────────────────────────────
@superadmin_bp.route("/")
@superadmin_required
def dashboard():
    restaurants = Restaurant.query.order_by(Restaurant.name).all()
    users = User.query.order_by(User.email).all()
    return render_template("dashboard.html", restaurants=restaurants, users=users)


# ── restaurant CRUD ──────────────────────────────────────────────────────────
def _slugify(name):
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    return re.sub(r"[\s_]+", "-", slug).strip("-")


@superadmin_bp.route("/restaurant/new", methods=["GET", "POST"])
@superadmin_required
def restaurant_new():
    if request.method == "POST":
        name = request.form["name"].strip()
        slug = request.form.get("slug", "").strip() or _slugify(name)
        tagline = request.form.get("tagline", "").strip()
        brand_color = request.form.get("brand_color", "#c9a84c").strip()
        brand_color_dim = request.form.get("brand_color_dim", "#a68939").strip()

        if not name:
            flash("Name is required.", "error")
            return render_template("restaurant_form.html", restaurant=None)
        if Restaurant.query.filter_by(slug=slug).first():
            flash(f"Slug '{slug}' is already taken.", "error")
            return render_template("restaurant_form.html", restaurant=None)

        r = Restaurant(
            name=name, slug=slug, tagline=tagline,
            brand_color=brand_color, brand_color_dim=brand_color_dim,
        )
        db.session.add(r)
        db.session.commit()
        flash(f"Restaurant '{name}' created.", "success")
        return redirect(url_for("superadmin.dashboard"))
    return render_template("restaurant_form.html", restaurant=None)


@superadmin_bp.route("/restaurant/<int:restaurant_id>/edit", methods=["GET", "POST"])
@superadmin_required
def restaurant_edit(restaurant_id):
    r = db.get_or_404(Restaurant, restaurant_id)
    if request.method == "POST":
        r.name = request.form["name"].strip()
        new_slug = request.form.get("slug", "").strip() or _slugify(r.name)
        if new_slug != r.slug:
            if Restaurant.query.filter_by(slug=new_slug).first():
                flash(f"Slug '{new_slug}' is already taken.", "error")
                return render_template("restaurant_form.html", restaurant=r)
            r.slug = new_slug
        r.tagline = request.form.get("tagline", "").strip()
        r.brand_color = request.form.get("brand_color", r.brand_color).strip()
        r.brand_color_dim = request.form.get("brand_color_dim", r.brand_color_dim).strip()
        db.session.commit()
        flash(f"Restaurant '{r.name}' updated.", "success")
        return redirect(url_for("superadmin.dashboard"))
    return render_template("restaurant_form.html", restaurant=r)


@superadmin_bp.route("/restaurant/<int:restaurant_id>/delete", methods=["POST"])
@superadmin_required
def restaurant_delete(restaurant_id):
    r = db.get_or_404(Restaurant, restaurant_id)
    name = r.name
    db.session.delete(r)
    db.session.commit()
    flash(f"Restaurant '{name}' and all its data deleted.", "success")
    return redirect(url_for("superadmin.dashboard"))


# ── user CRUD ────────────────────────────────────────────────────────────────
@superadmin_bp.route("/user/new", methods=["GET", "POST"])
@superadmin_required
def user_new():
    restaurants = Restaurant.query.order_by(Restaurant.name).all()
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]
        role = request.form.get("role", "owner")
        restaurant_id = request.form.get("restaurant_id") or None

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("user_form.html", user=None, restaurants=restaurants)
        if User.query.filter_by(email=email).first():
            flash(f"Email '{email}' already exists.", "error")
            return render_template("user_form.html", user=None, restaurants=restaurants)

        user = User(
            email=email,
            role=role,
            restaurant_id=int(restaurant_id) if restaurant_id else None,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f"User '{email}' created.", "success")
        return redirect(url_for("superadmin.dashboard"))
    return render_template("user_form.html", user=None, restaurants=restaurants)


@superadmin_bp.route("/user/<int:user_id>/edit", methods=["GET", "POST"])
@superadmin_required
def user_edit(user_id):
    user = db.get_or_404(User, user_id)
    restaurants = Restaurant.query.order_by(Restaurant.name).all()
    if request.method == "POST":
        user.email = request.form["email"].strip()
        user.role = request.form.get("role", user.role)
        restaurant_id = request.form.get("restaurant_id") or None
        user.restaurant_id = int(restaurant_id) if restaurant_id else None
        new_pw = request.form.get("password", "").strip()
        if new_pw:
            user.set_password(new_pw)
        db.session.commit()
        flash(f"User '{user.email}' updated.", "success")
        return redirect(url_for("superadmin.dashboard"))
    return render_template("user_form.html", user=user, restaurants=restaurants)


@superadmin_bp.route("/user/<int:user_id>/delete", methods=["POST"])
@superadmin_required
def user_delete(user_id):
    user = db.get_or_404(User, user_id)
    email = user.email
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{email}' deleted.", "success")
    return redirect(url_for("superadmin.dashboard"))
