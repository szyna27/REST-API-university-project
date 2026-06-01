import uuid
import pytest
import logging
from app.notifications.model.notification_orm import NotificationORM
from app.cart.model.order_orm import OrderORM
from app.cart.model.order_status import OrderStatus

logger = logging.getLogger(__name__)

def _setup_user(client):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    register_payload = {
        "email": email,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "first_name": "Test",
        "last_name": "User"
    }
    client.post("/api/v1/auth/register", json=register_payload)
    client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return email

def _setup_cart(client):
    email = _setup_user(client)
    product_payload = {
        "name": f"BasketProd{uuid.uuid4().hex[:8]}",
        "price": 799.99,
        "count": 50,
        "description": "Integration basket product",
        "category_id": 1
    }
    product_res = client.post("/api/v1/products", json=product_payload)
    product_id = product_res.json()["id"]
    client.post("/api/v1/cart/items", json={"product_id": product_id, "quantity": 1})
    return email

def _setup_order(client):
    email = _setup_cart(client)
    checkout_res = client.post("/api/v1/cart/checkout")
    order_id = checkout_res.json()["id"]
    return email, order_id


def test_1_registration_and_login(client, db_session):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    register_payload = {
        "email": email,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "first_name": "Test",
        "last_name": "User"
    }
    register_res = client.post("/api/v1/auth/register", json=register_payload)
    assert register_res.status_code == 201

    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    assert login_res.status_code == 200

def test_2_add_product_to_cart(client, db_session):
    _setup_user(client)
    product_payload = {
        "name": f"Prod{uuid.uuid4().hex[:8]}",
        "price": 799.99,
        "count": 10,
        "description": "Product for cart",
        "category_id": 1
    }
    product_res = client.post("/api/v1/products", json=product_payload)
    assert product_res.status_code == 201

    add_item_res = client.post("/api/v1/cart/items", json={"product_id": product_res.json()["id"], "quantity": 2})
    assert add_item_res.status_code == 201

def test_3_checkout(client, db_session):
    _setup_cart(client)
    checkout_res = client.post("/api/v1/cart/checkout")
    assert checkout_res.status_code == 201

def test_4_create_order(client, db_session):
    _setup_cart(client)
    checkout_res = client.post("/api/v1/cart/checkout")
    checkout_data = checkout_res.json()
    assert "id" in checkout_data
    assert checkout_data["status"] == "PENDING"
    
    # Dodatkowa weryfikacja czy utworzone zamówienie istnieje
    orders_res = client.get("/api/v1/orders")
    assert orders_res.status_code == 200
    assert any(o["id"] == checkout_data["id"] for o in orders_res.json())

def test_5_complete_order(client, db_session):
    email, order_id = _setup_order(client)
    idempotency_key = str(uuid.uuid4())
    complete_res = client.post(
        f"/api/v1/orders/{order_id}/complete",
        headers={"Idempotency-Key": idempotency_key}
    )
    assert complete_res.status_code == 200

def test_6_status_changed_to_completed(client, db_session):
    email, order_id = _setup_order(client)
    idempotency_key = str(uuid.uuid4())
    client.post(
        f"/api/v1/orders/{order_id}/complete",
        headers={"Idempotency-Key": idempotency_key}
    )
    order_in_db = db_session.query(OrderORM).filter(OrderORM.id == order_id).first()
    assert order_in_db.status == OrderStatus.COMPLETED

def test_7_idempotency_key_working(client, db_session):
    email, order_id = _setup_order(client)
    idempotency_key = str(uuid.uuid4())
    client.post(
        f"/api/v1/orders/{order_id}/complete",
        headers={"Idempotency-Key": idempotency_key}
    )
    complete_res_again = client.post(
        f"/api/v1/orders/{order_id}/complete",
        headers={"Idempotency-Key": idempotency_key}
    )
    assert complete_res_again.status_code == 200
    assert complete_res_again.json()["id"] == order_id

def test_8_block_different_idempotency_key(client, db_session):
    email, order_id = _setup_order(client)
    idempotency_key = str(uuid.uuid4())
    client.post(
        f"/api/v1/orders/{order_id}/complete",
        headers={"Idempotency-Key": idempotency_key}
    )
    different_idempotency_key = str(uuid.uuid4())
    complete_res_diff_key = client.post(
        f"/api/v1/orders/{order_id}/complete",
        headers={"Idempotency-Key": different_idempotency_key}
    )
    assert complete_res_diff_key.status_code == 400

def test_9_notifications_created(client, db_session):
    email, order_id = _setup_order(client)
    idempotency_key = str(uuid.uuid4())
    client.post(
        f"/api/v1/orders/{order_id}/complete",
        headers={"Idempotency-Key": idempotency_key}
    )
    notifications = client.get("/api/v1/notifications").json()
    
    email_notifications = [n for n in notifications if n['channel'] == "EMAIL" and n['recipient'] == email]
    push_notifications = [n for n in notifications if n['channel'] == "PUSH" and n['recipient'] == "test"]

    for n in email_notifications + push_notifications:
        send_response = client.post(f"/api/v1/notifications/{n['id']}/send-now")
        print(send_response.json())
        assert send_response.status_code == 200

    assert len(email_notifications) > 0, "Brak powiadomienia EMAIL o zakończeniu zamówienia"
    assert len(push_notifications) > 0, "Brak powiadomienia PUSH o zakończeniu zamówienia"