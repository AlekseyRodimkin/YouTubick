from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config.logging_config import logger

from .routes.main import main_router
from .routes.download import download_router

app_logger = logger.bind(name="app")

app = FastAPI()


@app.on_event("startup")
async def startup():
    """Function before launching the app (create tables)"""
    app_logger.debug("✅ App is started ✅")


@app.on_event("shutdown")
async def shutdown():
    """Function before the end of the application (close connection, session)"""
    app_logger.debug("‼️ App is stopped ‼️")


app.include_router(main_router)
app.include_router(download_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/api/healthchecker")
def root():
    app_logger.info(" app.get('/api/healthchecker') ")
    return {"message": "The API is LIVE!!"}
