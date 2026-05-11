# service/product_validators.py
from ..data.products_repository import get_product_by_name
from ..data.categories_repository import get_category_by_id
from ..data.forbidden_names_repository import get_all_forbidden_names

class ValidationError(Exception):
    pass

class ConflictError(Exception):
    pass

class ResourceNotFoundError(Exception):
    pass

def validate_product_name_length(name: str):
    if not (3 <= len(name) <= 20):
        raise ValidationError("Nazwa produktu musi mieć długość od 3 do 20 znaków.")
    
def validate_product_name_uniqueness(db, name: str, product_id: int = None):
    existing_product = get_product_by_name(db, name)
    if existing_product and existing_product.id != product_id:
        raise ConflictError("Produkt o takiej nazwie już istnieje.")
    
def validate_product_name_only_allowed_characters(name: str):
    if not name.isalnum():
        raise ValidationError("Nazwa produktu może zawierać tylko litery i cyfry.")

def validate_product_name_forbidden(db, name: str):
    rows = get_all_forbidden_names(db)
    name_lower = name.lower()
    for row in rows:
        if row.name.lower() in name_lower:
            raise ValidationError("Nazwa produktu zawiera zakazaną frazę.")

def validate_category_exists(db, category_id: int):
    category = get_category_by_id(db, category_id)
    if category is None:
        raise ResourceNotFoundError("Kategoria produktu nie istnieje.")
    return category

def validate_count_non_negative(count: int):
    if count < 0:
        raise ValidationError("Liczba produktów nie może być ujemna.")

def validate_price_range(category, price: float):
    if price < category.min_price or price > category.max_price:
        raise ValidationError("Cena produktu wykracza poza zakres dopuszczalny dla kategorii.")
