from fastapi import FastAPI
from routes import router
from post_routes import router as post_router
from stats_routes import router as stats_router

app = FastAPI(title="API Gateway", description="Proxy for User Service")

app.include_router(router, prefix="/api/users", tags=["Users"])
app.include_router(post_router, prefix="/api/posts", tags=["Posts"])
app.include_router(stats_router,  prefix="/api/stats", tags=["Statistics"])
