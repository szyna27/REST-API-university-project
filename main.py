from fastapi import FastAPI
from contextlib import asynccontextmanager
from threading import Thread

from app.REST.web.routes import router as products_router
from app.REST.docs_app import products_docs_app

from app.notifications.web.routes import router as notifications_router
from app.notifications.docs_app import notifications_docs_app
from app.notifications.service.notification_worker import run_worker

from app.identity.web.routes import router as identity_router
from app.identity.docs_app import identity_docs_app

from app.cart.web.routes import router as cart_router
from app.cart.docs_app import cart_docs_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = Thread(target=run_worker, daemon=True)
    thread.start()
    yield

app = FastAPI(
    title="Projekt - REST API", 
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(products_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(identity_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.mount("/products-docs", products_docs_app)
app.mount("/notifications-docs", notifications_docs_app)
app.mount("/identity-docs", identity_docs_app)
app.mount("/cart-docs", cart_docs_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
