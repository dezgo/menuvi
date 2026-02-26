from menuvi.models import Category, MenuItem

SLUG = "test-restaurant"


def _login(client, email="admin@test.com", password="testpass"):
    return client.post(
        f"/{SLUG}/admin/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_admin_login_required(client, restaurant):
    resp = client.get(f"/{SLUG}/admin/")
    assert resp.status_code == 302


def test_admin_login_success(client, restaurant, admin_user):
    resp = _login(client)
    assert resp.status_code == 200
    assert b"Menu Manager" in resp.data


def test_admin_login_wrong_password(client, restaurant, admin_user):
    resp = _login(client, password="wrong")
    assert b"Invalid email or password" in resp.data


def test_create_category(client, restaurant, admin_user):
    _login(client)
    resp = client.post(
        f"/{SLUG}/admin/category/new",
        data={"name": "Desserts", "menu_type": "dining", "sort_order": "5"},
        follow_redirects=True,
    )
    assert b"Desserts" in resp.data


def test_create_item(client, app, db, restaurant, admin_user):
    _login(client)
    client.post(
        f"/{SLUG}/admin/category/new",
        data={"name": "Mains", "menu_type": "dining", "sort_order": "0"},
    )
    with app.app_context():
        cat = Category.query.filter_by(restaurant_id=restaurant.id).first()
        cat_id = cat.id

    resp = client.post(
        f"/{SLUG}/admin/category/{cat_id}/item/new",
        data={
            "name": "Lamb Rogan Josh",
            "description": "Northern Indian delicacy",
            "price": "21.90",
            "sort_order": "0",
            "available": "on",
        },
        follow_redirects=True,
    )
    assert b"Lamb Rogan Josh" in resp.data


def test_toggle_availability(client, app, db, restaurant, admin_user):
    _login(client)
    client.post(
        f"/{SLUG}/admin/category/new",
        data={"name": "Mains", "menu_type": "dining", "sort_order": "0"},
    )
    with app.app_context():
        cat = Category.query.filter_by(restaurant_id=restaurant.id).first()
        cat_id = cat.id

    client.post(
        f"/{SLUG}/admin/category/{cat_id}/item/new",
        data={"name": "Test Item", "price": "10", "sort_order": "0", "available": "on"},
    )

    with app.app_context():
        item = MenuItem.query.first()
        item_id = item.id
        assert item.available is True

    client.post(f"/{SLUG}/admin/item/{item_id}/toggle")

    with app.app_context():
        item = db.session.get(MenuItem, item_id)
        assert item.available is False
