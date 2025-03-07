from fastapi import FastAPI
from routes import router

app = FastAPI(title="API Gateway", description="Proxy for User Service")

app.include_router(router, prefix="/api/users", tags=["Users"])
