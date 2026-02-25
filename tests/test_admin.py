def _login(client, password="testpass"):
    return client.post(
        "/admin/login", data={"password": password}, follow_redirects=True,
    )


def test_admin_login_required(client):
    resp = client.get("/admin/")
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]


def test_admin_login_success(client):
    resp = _login(client)
    assert resp.status_code == 200
    assert b"Menu Manager" in resp.data


def test_admin_login_wrong_password(client):
    resp = _login(client, "wrong")
    assert b"Incorrect password" in resp.data


def test_create_category(client):
    _login(client)
    resp = client.post(
        "/admin/category/new",
        data={"name": "Desserts", "menu_type": "dining", "sort_order": "5"},
        follow_redirects=True,
    )
    assert b"Desserts" in resp.data


def test_create_item(client, app, db):
    _login(client)
    # Create category first
    client.post(
        "/admin/category/new",
        data={"name": "Mains", "menu_type": "dining", "sort_order": "0"},
    )
    from menuvi.models import Category
    with app.app_context():
        cat = Category.query.first()
        cat_id = cat.id

    resp = client.post(
        f"/admin/category/{cat_id}/item/new",
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


def test_toggle_availability(client, app, db):
    _login(client)
    client.post(
        "/admin/category/new",
        data={"name": "Mains", "menu_type": "dining", "sort_order": "0"},
    )
    from menuvi.models import Category, MenuItem
    with app.app_context():
        cat = Category.query.first()
        cat_id = cat.id

    client.post(
        f"/admin/category/{cat_id}/item/new",
        data={"name": "Test Item", "price": "10", "sort_order": "0", "available": "on"},
    )

    with app.app_context():
        item = MenuItem.query.first()
        item_id = item.id
        assert item.available is True

    client.post(f"/admin/item/{item_id}/toggle")

    with app.app_context():
        item = db.session.get(MenuItem, item_id)
        assert item.available is False
