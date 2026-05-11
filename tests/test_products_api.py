def build_product_payload() -> dict:
    return {
        "name": "ProductName",
        "price": 799.99,
        "count": 10,
        "description": "Product Description",
        "category_id": 1
    }


def test_get_products_returns_200_and_non_empty_list(client):
    response = client.get("/api/v1/products")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "price" in first
    assert "count" in first
    assert "description" in first
    assert "category" in first


def test_post_products_creates_product_and_history_entry(client):
    payload = build_product_payload()

    create_response = client.post("/api/v1/products", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()

    assert created["name"] == payload["name"]
    assert created["price"] == payload["price"]
    assert created["count"] == payload["count"]
    assert created["description"] == payload["description"]
    assert created["category"]["id"] == payload["category_id"]

    product_id = created["id"]

    history_response = client.get(f"/api/v1/products/{product_id}/history")
    assert history_response.status_code == 200

    history = history_response.json()
    assert isinstance(history, list)
    assert len(history) >= 1

    latest_entry = history[0]
    assert latest_entry["product_id"] == product_id
    assert latest_entry["action"] == "CREATE"
    assert latest_entry["previous_state"] == {}
    assert latest_entry["current_state"]["price"] == payload["price"]
    assert latest_entry["current_state"]["count"] == payload["count"]


def test_post_products_rejects_forbidden_name(client):
    payload = build_product_payload()
    payload["name"] = f"test{payload['name'].lower()}"

    response = client.post("/api/v1/products", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Nazwa produktu zawiera zakazaną frazę."


def test_post_products_rejects_product_name_with_invalid_length(client):
    payload = {
        "name": "ab",
        "price": 799.99,
        "count": 10,
        "description": "Product Description",
        "category_id": 1
    }

    response = client.post("/api/v1/products", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Nazwa produktu musi mieć długość od 3 do 20 znaków."


def test_post_products_rejects_price_out_of_range_for_category(client):
    payload = build_product_payload()
    payload["price"] = 10000.00  # Przykładowa cena poza zakresem
    payload["category_id"] = 1  # Zakładamy, że kategoria 1 ma określony zakres cenowy

    response = client.post("/api/v1/products", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Cena produktu wykracza poza zakres dopuszczalny dla kategorii."


def test_put_products_replaces_all_fields_and_saves_history(client):
    create_payload = build_product_payload()
    create_response = client.post("/api/v1/products", json=create_payload)
    assert create_response.status_code == 201
    
    created_product = create_response.json()
    product_id = created_product["id"]

    update_payload = {
        "name": "UpdatedName",
        "price": 899.99,
        "count": 15,
        "description": "Updated Description",
        "category_id": 1
    }

    update_response = client.put(f"/api/v1/products/{product_id}", json=update_payload)

    assert update_response.status_code == 200
    updated = update_response.json()

    assert updated["id"] == product_id
    assert updated["name"] == update_payload["name"]
    assert updated["price"] == update_payload["price"]
    assert updated["count"] == update_payload["count"]
    assert updated["description"] == update_payload["description"]
    assert updated["category"]["id"] == update_payload["category_id"]

    history_response = client.get(f"/api/v1/products/{product_id}/history")
    assert history_response.status_code == 200

    history = history_response.json()
    assert len(history) >= 2

    latest_entry = history[0]
    create_entry = history[1]

    assert latest_entry["action"] == "REPLACE"
    assert latest_entry["previous_state"]["name"] == create_payload["name"]
    assert latest_entry["current_state"]["name"] == update_payload["name"]
    assert latest_entry["previous_state"]["price"] == create_payload["price"]
    assert latest_entry["current_state"]["price"] == update_payload["price"]
    assert latest_entry["previous_state"]["count"] == create_payload["count"]
    assert latest_entry["current_state"]["count"] == update_payload["count"]
    assert latest_entry["previous_state"]["description"] == create_payload["description"]
    assert latest_entry["current_state"]["description"] == update_payload["description"]
    assert latest_entry["previous_state"]["category_id"] == create_payload["category_id"]
    assert latest_entry["current_state"]["category_id"] == update_payload["category_id"]

    assert create_entry["action"] == "CREATE"


def test_patch_products_updates_selected_fields_and_saves_history(client):
    create_payload = build_product_payload()
    create_response = client.post("/api/v1/products", json=create_payload)
    assert create_response.status_code == 201
    
    created_product = create_response.json()
    product_id = created_product["id"]

    patch_payload = {
        "price": 899.99,
        "count": 15,
    }

    patch_response = client.patch(f"/api/v1/products/{product_id}", json=patch_payload)

    assert patch_response.status_code == 200
    updated = patch_response.json()

    assert updated["id"] == product_id
    assert updated["price"] == patch_payload["price"]
    assert updated["count"] == patch_payload["count"]

    history_response = client.get(f"/api/v1/products/{product_id}/history")
    assert history_response.status_code == 200

    history = history_response.json()
    assert len(history) >= 2

    latest_entry = history[0]
    create_entry = history[1]

    assert latest_entry["action"] == "UPDATE"
    assert latest_entry["previous_state"]["price"] == create_payload["price"]
    assert latest_entry["current_state"]["price"] == patch_payload["price"]
    assert latest_entry["previous_state"]["count"] == create_payload["count"]
    assert latest_entry["current_state"]["count"] == patch_payload["count"]

    assert create_entry["action"] == "CREATE"


def test_delete_products_returns_204_and_product_is_no_longer_available(client):
    create_payload = build_product_payload()
    create_response = client.post("/api/v1/products", json=create_payload)
    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    get_response = client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Product not found"