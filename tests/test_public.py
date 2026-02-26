from menuvi.models import Category, MenuItem, db

SLUG = "test-restaurant"


def _seed(db_session, restaurant):
    cat = Category(
        restaurant_id=restaurant.id, name="Mains", menu_type="dining", sort_order=0,
    )
    db_session.add(cat)
    db_session.flush()
    item = MenuItem(
        category_id=cat.id, name="Butter Chicken",
        description="Creamy tomato sauce", price_cents=2290, sort_order=0,
    )
    db_session.add(item)
    db_session.commit()
    return cat, item


def test_directory_page(client, restaurant):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Test Restaurant" in resp.data


def test_landing_page(client, restaurant):
    resp = client.get(f"/{SLUG}/")
    assert resp.status_code == 200
    assert b"Dining Menu" in resp.data
    assert b"Beverages" in resp.data


def test_menu_page(client, app, restaurant):
    with app.app_context():
        _seed(db.session, restaurant)
    resp = client.get(f"/{SLUG}/menu/dining")
    assert resp.status_code == 200
    assert b"Mains" in resp.data


def test_category_page(client, app, restaurant):
    with app.app_context():
        cat, item = _seed(db.session, restaurant)
        cat_id = cat.id
    resp = client.get(f"/{SLUG}/category/{cat_id}")
    assert resp.status_code == 200
    assert b"Butter Chicken" in resp.data


def test_item_detail(client, app, restaurant):
    with app.app_context():
        _, item = _seed(db.session, restaurant)
        item_id = item.id
    resp = client.get(f"/{SLUG}/item/{item_id}")
    assert resp.status_code == 200
    assert b"Butter Chicken" in resp.data
    assert b"$22.90" in resp.data


def test_search(client, app, restaurant):
    with app.app_context():
        _seed(db.session, restaurant)
    resp = client.get(f"/{SLUG}/search?q=butter")
    assert resp.status_code == 200
    assert b"Butter Chicken" in resp.data


def test_search_no_results(client, app, restaurant):
    with app.app_context():
        _seed(db.session, restaurant)
    resp = client.get(f"/{SLUG}/search?q=pizza")
    assert resp.status_code == 200
    assert b"No items found" in resp.data
