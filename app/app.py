from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from .routes.live_play import live_router
from .routes.main import main_router

app = FastAPI()


@app.on_event("startup")
async def startup():
    """Function before launching the app (create tables)"""
    print("✅ App is started ✅")


@app.on_event("shutdown")
async def shutdown():
    """Function before the end of the application (close connection, session)"""
    print("‼️ App is stopped ‼️")


app.include_router(main_router)
app.include_router(live_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/healthchecker", status_code=200, response_class=JSONResponse)
def root():
    return
