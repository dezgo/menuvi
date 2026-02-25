from menuvi.models import Category, MenuItem, db


def _seed(db_session):
    cat = Category(name="Mains", menu_type="dining", sort_order=0)
    db_session.add(cat)
    db_session.flush()
    item = MenuItem(
        category_id=cat.id, name="Butter Chicken",
        description="Creamy tomato sauce", price_cents=2290, sort_order=0,
    )
    db_session.add(item)
    db_session.commit()
    return cat, item


def test_landing_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Dining Menu" in resp.data
    assert b"Beverages" in resp.data


def test_menu_page(client, app):
    with app.app_context():
        _seed(db.session)
    resp = client.get("/menu/dining")
    assert resp.status_code == 200
    assert b"Mains" in resp.data


def test_category_page(client, app):
    with app.app_context():
        cat, item = _seed(db.session)
        cat_id = cat.id
    resp = client.get(f"/category/{cat_id}")
    assert resp.status_code == 200
    assert b"Butter Chicken" in resp.data


def test_item_detail(client, app):
    with app.app_context():
        _, item = _seed(db.session)
        item_id = item.id
    resp = client.get(f"/item/{item_id}")
    assert resp.status_code == 200
    assert b"Butter Chicken" in resp.data
    assert b"$22.90" in resp.data


def test_search(client, app):
    with app.app_context():
        _seed(db.session)
    resp = client.get("/search?q=butter")
    assert resp.status_code == 200
    assert b"Butter Chicken" in resp.data


def test_search_no_results(client, app):
    with app.app_context():
        _seed(db.session)
    resp = client.get("/search?q=pizza")
    assert resp.status_code == 200
    assert b"No items found" in resp.data
