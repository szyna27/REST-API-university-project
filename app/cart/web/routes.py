from fastapi import APIRouter, Cookie, Depends, HTTPException, Header, Path, status
from sqlalchemy.orm import Session
from app.REST.data.database import get_db
from app.identity.model.operator_orm import OperatorORM
from app.identity.service.auth_exceptions import AuthorizationError
from app.identity.service.auth_service import get_current_operator
from app.cart.model.cart_schema import (
    ShoppingCartItemCreate,
    ShoppingCartItemUpdate,
    ShoppingCartResponse,
    OrderListItemResponse,
    OrderResponse,
)
from app.cart.service.cart_exceptions import (
    CartConflictError,
    CartNotFoundError,
    CartValidationError,
    OrderNotFoundError,
)
from app.cart.service.cart_service import (
    add_product_to_shopping_cart,
    edit_product_in_shopping_cart,
    get_current_shopping_cart,
    remove_product_from_shopping_cart,
)
from app.cart.service.order_query_service import list_orders, get_order_details, get_dashboard_summary
from app.cart.service.confirm_order_command import ConfirmOrderCommand
from app.cart.service.confirm_order_handler import handle_confirm_order
from app.cart.service.complete_order_command import CompleteOrderCommand
from app.cart.service.complete_order_handler import handle_complete_order

router = APIRouter(
    tags=["Shopping Cart"],
)

def get_current_operator_dependency(
    auth_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> OperatorORM:
    if auth_token is None:
        raise HTTPException(status_code=401, detail="Brak aktywnej sesji.")

    try:
        return get_current_operator(db, auth_token)

    except AuthorizationError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get(
    "/cart",
    response_model=ShoppingCartResponse,
    status_code=status.HTTP_200_OK,
)
def get_shopping_cart_endpoint(
    operator: OperatorORM = Depends(get_current_operator_dependency),
    db: Session = Depends(get_db),
):
    return get_current_shopping_cart(
        db=db,
        operator_id=operator.id,
    )

@router.post(
    "/cart/items",
    response_model=ShoppingCartResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_cart_item_endpoint(
    payload: ShoppingCartItemCreate,
    operator: OperatorORM = Depends(get_current_operator_dependency),
    db: Session = Depends(get_db),
):
    try:
        return add_product_to_shopping_cart(
            db=db,
            operator_id=operator.id,
            payload=payload,
        )
    except CartNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CartConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch(
    "/cart/items/{item_id}",
    response_model=ShoppingCartResponse,
    status_code=status.HTTP_200_OK,
)
def edit_cart_item_endpoint(
    payload: ShoppingCartItemUpdate,
    item_id: int = Path(..., gt=0),
    operator: OperatorORM = Depends(get_current_operator_dependency),
    db: Session = Depends(get_db),
):
    try:
        return edit_product_in_shopping_cart(
            db=db,
            operator_id=operator.id,
            item_id=item_id,
            quantity=payload.quantity,
        )
    except CartNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CartConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete(
    "/cart/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_cart_item_endpoint(
    item_id: int = Path(..., gt=0),
    operator: OperatorORM = Depends(get_current_operator_dependency),
    db: Session = Depends(get_db),
):
    try:
        remove_product_from_shopping_cart(
            db=db,
            operator_id=operator.id,
            item_id=item_id,
        )
        return
    except CartNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post(
    "/cart/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def confirm_order_endpoint(
    operator: OperatorORM = Depends(get_current_operator_dependency),
    db: Session = Depends(get_db),
):
    command = ConfirmOrderCommand(operator_id=operator.id)
    try:
        return handle_confirm_order(
            db=db,
            command=command,
        )
    except CartValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/orders",
    response_model=list[OrderListItemResponse],
    status_code=status.HTTP_200_OK,
)
def list_orders_endpoint(
    operator: OperatorORM = Depends(get_current_operator_dependency),
    db: Session = Depends(get_db),
):
    return list_orders(
        db=db,
        operator_id=operator.id,
    )

@router.get(
    "/orders/dashboard/summary",
    status_code=status.HTTP_200_OK,
)
def get_dashboard_summary_endpoint(
    operator: OperatorORM = Depends(get_current_operator_dependency),
    db: Session = Depends(get_db),
):
    return get_dashboard_summary(
        db=db,
        operator_id=operator.id,
    )

@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
def get_order_details_endpoint(
    order_id: int = Path(..., gt=0),
    operator: OperatorORM = Depends(get_current_operator_dependency),
    db: Session = Depends(get_db),
):
    try:
        return get_order_details(
            db=db,
            operator_id=operator.id,
            order_id=order_id,
        )
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.post(
    "/orders/{order_id}/complete",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
def complete_Order_endpoint(
    order_id: int = Path(..., gt=0),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    operator: OperatorORM = Depends(get_current_operator_dependency),
    db: Session = Depends(get_db),
):
    command = CompleteOrderCommand(
        operator_id=operator.id,
        order_id=order_id,
        idempotency_key=idempotency_key,
        ordered_by=operator.email,
        source="API",
        notify_email=True,
        notify_push=True,
        note="Przypisanie zakończone przez operatora.",
    )

    try:
        return handle_complete_order(
            db=db,
            command=command,
        )

    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except CartValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))