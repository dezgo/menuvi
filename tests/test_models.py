from menuvi.models import Category, MenuItem


def test_price_display():
    item = MenuItem(name="Test", price_cents=2290)
    assert item.price_display == "$22.90"


def test_price_display_none():
    item = MenuItem(name="Test", price_cents=None)
    assert item.price_display == ""


def test_category_creation(db):
    cat = Category(name="Mains", menu_type="dining", sort_order=0)
    db.session.add(cat)
    db.session.commit()

    assert cat.id is not None
    assert cat.name == "Mains"
    assert cat.menu_type == "dining"


def test_item_belongs_to_category(db):
    cat = Category(name="Starters", sort_order=0)
    db.session.add(cat)
    db.session.flush()

    item = MenuItem(
        category_id=cat.id, name="Samosa", description="Crispy", price_cents=1290,
    )
    db.session.add(item)
    db.session.commit()

    assert item.category.name == "Starters"
    assert len(cat.items) == 1
