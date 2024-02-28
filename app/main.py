from fastapi import FastAPI, APIRouter
from app.settings import settings
from schedule.routers import schedule_router
from users.routers import user_router, session_router
from datetime import datetime, timezone
import uvicorn

app = FastAPI()

base_router = APIRouter(tags=['base'])

routers = [base_router, session_router, user_router, schedule_router]

@base_router.get("/")
def status(test_query: str = "none"):
    return {
        "version": settings.app.VERSION,
        "name": settings.app.NAME,
        "status": "ok",
        "env": settings.app.ENV,
        "datetime": datetime.utcnow().strftime(settings.app.DATE_FORMAT)
    }

[app.include_router(router, prefix=settings.app.URL_PREFIX) for router in routers]

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.app.HOST, port=settings.app.PORT, reload=settings.app.ENV == "development")

