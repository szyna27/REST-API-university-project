from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..service.product_validators import ValidationError, ConflictError, ResourceNotFoundError
from ..service.product_service import (
    list_product_history,
    list_products,
    get_single_product,
    create_product,
    replace_product,
    patch_product,
    remove_product,
)
from ..data.database import get_db
from ..model.product_schema import Product, ProductCreate, ProductUpdate
from ..model.product_history_schema import ProductHistoryEntry

router = APIRouter(tags=["Products"])

@router.get("/products", response_model=list[Product]) #list[ProductORM] -> list[Product] -> json
def get_products(db: Session = Depends(get_db)):
    return list_products(db)

@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = get_single_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(payload: ProductCreate, db: Session = Depends(get_db)):
    try:
        return create_product(db, payload)
    
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/products/{product_id}", response_model=Product)
def update_product_endpoint(product_id: int, payload: ProductCreate, db: Session = Depends(get_db)):
    try:
        product = replace_product(db, product_id, payload)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product
    
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.patch("/products/{product_id}", response_model=Product)
def patch_product_endpoint(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    try:
        product = patch_product(db, product_id, payload)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product
    
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    if not remove_product(db, product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return None

@router.get("/products/{id}/history", response_model=list[ProductHistoryEntry])
def get_product_history_endpoint(id: int, db: Session = Depends(get_db)):
    history = list_product_history(db, id)
    if history is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return history