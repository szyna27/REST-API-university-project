# service/product_service.py
from decimal import Decimal

from sqlalchemy.orm import Session

from app.REST.data.categories_repository import get_category_by_id

from ..data.product_history_repository import add_product_history, get_product_history_by_product_id
from ..data.products_repository import (
    get_all_products,
    get_product_by_id,
    add_product,
    update_product,
    delete_product,
)
from ..model.product_history_orm import ProductHistoryORM
from ..model.product_orm import ProductORM
from ..model.product_schema import ProductCreate, ProductUpdate
from ..service.product_validators import (
    validate_product_name_length,
    validate_product_name_uniqueness,
    validate_product_name_only_allowed_characters,
    validate_product_name_forbidden,
    validate_category_exists,
    validate_count_non_negative,
    validate_price_range,
)

def _validate_product_full_data(db: Session, payload: ProductCreate, product_id: int | None = None):
    """
    Prywatna metoda pomocnicza do pełnej walidacji danych produktu (Zasada DRY).
    Konsoliduje reguły wymagane przy operacjach POST i PUT.
    """
    # Walidacja tożsamości (Nazwa produktu: długość, znaki, unikalność)
    validate_product_name_length(payload.name)
    validate_product_name_only_allowed_characters(payload.name)
    validate_product_name_uniqueness(db, payload.name, product_id)
    validate_product_name_forbidden(db, payload.name)
    
    # Walidacja powiązań (Sprawdzenie czy kategoria istnieje)
    category = validate_category_exists(db, payload.category_id)
    
    # Walidacja count i price (Nieujemność oraz zgodność z zakresem kierunku)
    validate_count_non_negative(payload.count)
    validate_price_range(category, payload.price)
    
    return category  # Zwracamy kategorię, by uniknąć ponownego zapytania w serwisie tworzenia/aktualizacji produktu

def _validate_product_given_fields(db: Session, payload: ProductUpdate, product_id: int = None):
    """
    Prywatna metoda pomocnicza do walidacji tylko tych pól, które zostały przesłane (Zasada DRY).
    Używana w operacji PATCH, gdzie aktualizujemy tylko część danych produktu.
    """
    if payload.name is not None:
        validate_product_name_length(payload.name)
        validate_product_name_only_allowed_characters(payload.name)
        validate_product_name_uniqueness(db, payload.name, product_id)
        validate_product_name_forbidden(db, payload.name)
    
    if payload.category_id is not None:
        validate_category_exists(db, payload.category_id)
    
    if payload.count is not None:
        validate_count_non_negative(payload.count)
    
    if payload.price is not None and payload.category_id is not None:
        category = get_category_by_id(db, payload.category_id)
        validate_price_range(category, payload.price)
    elif payload.price is not None:
        category = get_category_by_id(db, get_product_by_id(db, product_id).category_id)
        validate_price_range(category, payload.price)

def list_products(db: Session):
    # Pobranie listy wszystkich produktów z repozytorium
    return get_all_products(db)

def get_single_product(db: Session, product_id: int):
    # Pobranie konkretnego produktu po ID (Web Layer obsłuży None jako 404)
    return get_product_by_id(db, product_id)

def create_product(db: Session, payload: ProductCreate):
    # Wykonanie pełnego zestawu walidacji przed utworzeniem
    _validate_product_full_data(db, payload)

    # Tworzenie obiektu ORM na podstawie przesłanych danych
    product = ProductORM(
        name=payload.name,
        price=payload.price,
        count=payload.count,
        description=payload.description,
        category_id=payload.category_id,
    )

    created_product = add_product(db, product)

    current_state = _build_product_snapshot(created_product)

    _save_product_history(
        db=db,
        product_id=created_product.id,
        previous_state={},
        current_state=current_state,
        action="CREATE",
    ) # utworzenie wpisu historii dla operacji CREATE

    # Dodanie produktu do bazy danych przez warstwę repozytorium
    return created_product

def replace_product(db: Session, product_id: int, payload: ProductCreate):
    # Sprawdzenie, czy zasób do aktualizacji (PUT) w ogóle istnieje
    product = get_single_product(db, product_id)
    if product is None:
        return None  # Sygnał dla Routes do rzucenia 404
    
    previous_state = _build_product_snapshot(product) # zapis stanu obiektu przed modyfikacją

    # Pełna walidacja nowych danych (przekazujemy product_id, by zignorować autokolizję po id)
    _validate_product_full_data(db, payload, product_id)

    # Nadpisanie wszystkich pól istniejącego obiektu ORM
    product.name = payload.name
    product.price = payload.price
    product.count = payload.count
    product.description = payload.description
    product.category_id = payload.category_id

    replaced_product = update_product(db, product)

    current_state = _build_product_snapshot(replaced_product)  # zapis stanu obiektu po modyfikacji

    _save_product_history(
        db=db,
        product_id=replaced_product.id,
        previous_state=previous_state,
        current_state=current_state,
        action="REPLACE",
    ) # utworzenie wpisu historii dla operacji REPLACE

    # Trwałe zapisanie zmian w bazie danych
    return replaced_product

def patch_product(db: Session, product_id: int, payload: ProductUpdate):
    product = get_single_product(db, product_id)
    if product is None:
        return None

    previous_state = _build_product_snapshot(product) # zapis stanu obiektu przed modyfikacją

    #logika walidacyjna
    _validate_product_given_fields(db, payload, product_id)
    # Aktualizacja tylko tych pól, które zostały przesłane (nie-None)
    if payload.name is not None:
        product.name = payload.name
    if payload.price is not None:
        product.price = payload.price
    if payload.count is not None:
        product.count = payload.count
    if payload.description is not None:
        product.description = payload.description
    if payload.category_id is not None:
        product.category_id = payload.category_id

    updated_product = update_product(db, product)

    current_state = _build_product_snapshot(updated_product)  # zapis stanu obiektu po modyfikacji

    _save_product_history(
        db=db,
        product_id=updated_product.id,
        previous_state=previous_state,
        current_state=current_state,
        action="UPDATE",
    ) # utworzenie wpisu historii dla operacji UPDATE

    return updated_product

def remove_product(db: Session, product_id: int):
    # Sprawdzenie, czy produkt do usunięcia istnieje w bazie
    product = get_single_product(db, product_id)

    if product is None:
        # Sygnał dla warstwy Web: nie można usunąć czegoś, czego nie ma
        return False
    
    previous_state = _build_product_snapshot(product) # zapis stanu obiektu przed usunięciem

    # Wywołanie fizycznego usunięcia rekordu w warstwie danych
    delete_product(db, product)

    # Zapisanie wpisu historii dla operacji DELETE
    _save_product_history(
        db=db,
        product_id=product.id,
        previous_state=previous_state,
        current_state={},
        action="DELETE",
    )

    # Zwrócenie sukcesu operacji (Web Layer odpowie statusem 204)
    return True

def _build_product_snapshot(product: ProductORM) -> dict:
    snapshot = {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "count": product.count,
        "description": product.description,
        "category_id": product.category_id,
        "category": {
            "id": product.category.id,
            "name": product.category.name,
            "min_price": product.category.min_price,
            "max_price": product.category.max_price,
        }
    }

    return _to_json_safe(snapshot)


def _to_json_safe(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, dict):
        return {k: _to_json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [_to_json_safe(v) for v in value]

    return value

def _save_product_history(
    db: Session,
    product_id: int | None,
    previous_state: dict,
    current_state: dict,
    action: str,
):
    history_entry = ProductHistoryORM(
        product_id=product_id,
        action=action,
        previous_state=previous_state,
        current_state=current_state,
    )
    return add_product_history(db, history_entry)

def list_product_history(db: Session, product_id: int):
    # Najpierw sprawdzamy, czy produkt istnieje. Jeśli nie, Web Layer zwróci 404.
    product = get_product_by_id(db, product_id)
    if product is None:
        return None

    # Pobranie historii zmian dla danego produktu
    return get_product_history_by_product_id(db, product_id)
