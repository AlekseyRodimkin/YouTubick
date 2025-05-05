from fastapi import APIRouter, Request, Form
from config.logging_config import logger
from config.config import templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.services.utils import is_valid_youtube_url

main_router = APIRouter(prefix="", tags=["main"])
app_logger = logger.bind(name="app")


@main_router.get("/", status_code=200, response_class=HTMLResponse)
async def index(request: Request, message=None):
    try:
        app_logger.info(f"GET/")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Главная страница",
                "messages": [message] if message else []
            }
        )
    except Exception as e:
        app_logger.error(f"{e}")
        return 500


@main_router.post("/")
async def post_index(request: Request,
                     action: str = Form(...),
                     url: str = Form(...)):
    try:
        app_logger.info(f"POST/ with action: {action} and URL: {url}")

        if not  await is_valid_youtube_url(url):
            return await index(request, "Некорректная YouTube ссылка")

        if action == "download":
            return RedirectResponse(url=f"/download?url={url}")
        elif action == "long_play":
            return RedirectResponse(url=f"/long-view?url={url}")
        elif action == "fast_play":
            return RedirectResponse(url=f"/live?url={url}")

    except Exception as e:
        app_logger.error(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Внутренняя ошибка сервера"}
        )
