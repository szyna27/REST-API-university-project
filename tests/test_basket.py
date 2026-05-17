import uuid
import pytest
from app.notifications.model.notification_orm import NotificationORM
from app.cart.model.order_orm import OrderORM
from app.cart.model.order_status import OrderStatus

def test_full_basket_process(client, db_session):
    # 1. Rejestracja
    register_payload = {
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "first_name": "Test",
        "last_name": "User"
    }
    register_res = client.post("/api/v1/auth/register", json=register_payload)
    assert register_res.status_code == 201

    # 1a. Logowanie
    login_payload = {
        "email": register_payload["email"],
        "password": register_payload["password"]
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    
    # 2. Utworzenie produktu do koszyka
    product_payload = {
        "name": "SuperKoszyk",
        "price": 799.99,
        "count": 50,
        "description": "Integration basket product",
        "category_id": 1
    }
    product_res = client.post("/api/v1/products", json=product_payload)
    assert product_res.status_code == 201, product_res.json()
    product_id = product_res.json()["id"]

    # 3. Dodanie produktu do koszyka
    add_item_payload = {
        "product_id": product_id,
        "quantity": 2
    }
    add_item_res = client.post("/api/v1/cart/items", json=add_item_payload)
    assert add_item_res.status_code == 201
    
    # 4. Checkout (utworzenie zamówienia)
    checkout_res = client.post("/api/v1/cart/checkout")
    assert checkout_res.status_code == 201
    checkout_data = checkout_res.json()
    order_id = checkout_data["id"]

    # 5. Zakończenie zamówienia (zmiana statusu na COMPLETED)
    idempotency_key = str(uuid.uuid4())
    complete_res = client.post(
        f"/api/v1/orders/{order_id}/complete",
        headers={"Idempotency-Key": idempotency_key}
    )
    assert complete_res.status_code == 200, complete_res.json()
    assert complete_res.json()["status"] == "COMPLETED"

    # Weryfikacja zmiany statusu w bazie
    order_in_db = db_session.query(OrderORM).filter(OrderORM.id == order_id).first()
    assert order_in_db.status == OrderStatus.COMPLETED

    # 6. Sprawdzenie działania Idempotency-Key (ponowne wywołanie z tym samym kluczem)
    complete_res_again = client.post(
        f"/api/v1/orders/{order_id}/complete",
        headers={"Idempotency-Key": idempotency_key}
    )
    assert complete_res_again.status_code == 200
    assert complete_res_again.json()["id"] == order_id

    # 7. Blokada ponownego wykonania operacji z innym kluczem dla zakończonego zamówienia
    different_idempotency_key = str(uuid.uuid4())
    complete_res_diff_key = client.post(
        f"/api/v1/orders/{order_id}/complete",
        headers={"Idempotency-Key": different_idempotency_key}
    )
    assert complete_res_diff_key.status_code == 400

    # 8. Weryfikacja, że po zakończeniu zamówienia powstają powiadomienia EMAIL i PUSH
    notifications = db_session.query(NotificationORM).all()
    
    email_notifications = [n for n in notifications if n.channel == "EMAIL" and register_payload["email"] in n.recipient]
    push_notifications = [n for n in notifications if n.channel == "PUSH"]

    assert len(email_notifications) > 0, "Brak powiadomienia EMAIL o zakończeniu zamówienia"
    assert len(push_notifications) > 0, "Brak powiadomienia PUSH o zakończeniu zamówienia"