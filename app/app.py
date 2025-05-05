from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# from config.config import engine
from config.logging_config import logger

from .routes.main import main_router
from .routes.work import work_router

app_logger = logger.bind(name="app")

app = FastAPI()


@app.on_event("startup")
async def startup():
    """Function before launching the app (create tables)"""
    app_logger.debug("🔝 App is started 🔝")

    # async with engine.begin() as conn:
    #     await conn.run_sync(models.Base.metadata.create_all)
    #     app_logger.debug("🔄 Tables are created 🔄")


@app.on_event("shutdown")
async def shutdown():
    """Function before the end of the application (close connection, session)"""
    app_logger.debug("⤵️ App is stopped ⤵️")
    # await engine.dispose()


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
app.include_router(work_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/api/healthchecker")
def root():
    app_logger.info(" app.get('/api/healthchecker') ")
    return {"message": "The API is LIVE!!"}
