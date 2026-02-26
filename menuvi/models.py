from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    tagline = db.Column(db.String(300), default="")
    brand_color = db.Column(db.String(20), default="#c9a84c")
    brand_color_dim = db.Column(db.String(20), default="#a68939")

    categories = db.relationship(
        "Category", back_populates="restaurant", cascade="all, delete-orphan",
    )
    users = db.relationship(
        "User", back_populates="restaurant",
    )

    def __repr__(self):
        return f"<Restaurant {self.name!r}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="owner")  # "owner" or "superadmin"
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurants.id"), nullable=True,
    )

    restaurant = db.relationship("Restaurant", back_populates="users")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_superadmin(self):
        return self.role == "superadmin"

    def __repr__(self):
        return f"<User {self.email!r}>"


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        db.UniqueConstraint("restaurant_id", "name", name="uq_category_restaurant_name"),
    )

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurants.id"), nullable=False,
    )
    name = db.Column(db.String(120), nullable=False)
    menu_type = db.Column(db.String(20), default="dining")  # "dining" or "beverages"
    sort_order = db.Column(db.Integer, default=0)

    restaurant = db.relationship("Restaurant", back_populates="categories")
    items = db.relationship(
        "MenuItem", back_populates="category", cascade="all, delete-orphan",
        order_by="MenuItem.sort_order",
    )

    def __repr__(self):
        return f"<Category {self.name!r}>"


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False
    )
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    price_cents = db.Column(db.Integer, nullable=True)
    available = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    category = db.relationship("Category", back_populates="items")

    @property
    def price_display(self):
        if self.price_cents is None:
            return ""
        dollars = self.price_cents / 100
        return f"${dollars:,.2f}"

    def __repr__(self):
        return f"<MenuItem {self.name!r}>"
