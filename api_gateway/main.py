from fastapi import FastAPI
from routes import router
from post_routes import router as post_router

app = FastAPI(title="API Gateway", description="Proxy for User Service")

app.include_router(router, prefix="/api/users", tags=["Users"])
app.include_router(post_router, prefix="/api/posts", tags=["Posts"])
