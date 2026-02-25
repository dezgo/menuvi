from menuvi.models import Category, MenuItem, db


def _seed(db_session):
    cat = Category(name="Mains", menu_type="dining", sort_order=0)
    db_session.add(cat)
    db_session.flush()
    item = MenuItem(
        category_id=cat.id, name="Butter Chicken",
        description="Creamy", price_cents=2290, sort_order=0,
    )
    db_session.add(item)
    db_session.commit()
    return cat, item


def test_add_pick(client, app):
    with app.app_context():
        _, item = _seed(db.session)
        item_id = item.id

    resp = client.post(
        f"/picks/add/{item_id}",
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["count"] == 1


def test_add_pick_redirect(client, app):
    with app.app_context():
        _, item = _seed(db.session)
        item_id = item.id

    resp = client.post(f"/picks/add/{item_id}")
    assert resp.status_code == 302


def test_remove_pick(client, app):
    with app.app_context():
        _, item = _seed(db.session)
        item_id = item.id

    # Add first
    client.post(
        f"/picks/add/{item_id}",
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    # Remove
    resp = client.post(
        f"/picks/remove/{item_id}",
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    data = resp.get_json()
    assert data["ok"] is True
    assert data["count"] == 0


def test_picks_page_shows_items(client, app):
    with app.app_context():
        _, item = _seed(db.session)
        item_id = item.id

    client.post(f"/picks/add/{item_id}")
    resp = client.get("/picks")
    assert resp.status_code == 200
    assert b"Butter Chicken" in resp.data


def test_clear_picks(client, app):
    with app.app_context():
        _, item = _seed(db.session)
        item_id = item.id

    client.post(f"/picks/add/{item_id}")
    resp = client.post("/picks/clear", follow_redirects=True)
    assert resp.status_code == 200
    assert b"No picks yet" in resp.data


def test_duplicate_add(client, app):
    with app.app_context():
        _, item = _seed(db.session)
        item_id = item.id

    client.post(
        f"/picks/add/{item_id}",
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    resp = client.post(
        f"/picks/add/{item_id}",
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    data = resp.get_json()
    assert data["count"] == 1  # should not duplicate
