from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    menu_type = db.Column(db.String(20), default="dining")  # "dining" or "beverages"
    sort_order = db.Column(db.Integer, default=0)

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
