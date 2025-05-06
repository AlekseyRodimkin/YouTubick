from fastapi import APIRouter, Request, Form
from config.logging_config import logger
from config.config import templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.services.utils import is_valid_youtube_url

main_router = APIRouter(prefix="", tags=["main"])
app_logger = logger.bind(name="app")


@main_router.get("/", status_code=200, response_class=HTMLResponse)
async def index(request: Request, message=None, video_url=None):
    try:
        app_logger.info(f"GET/")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Главная страница",
                "messages": [{"status": message[0], "text": message[1]} if message else []],
                "video_url": video_url if video_url else None

            }
        )
    except Exception as e:
        # todo возврат ошибки
        return 500


@main_router.post("/")
async def post_index(request: Request):
    form = await request.form()
    url = form.get("url")
    action = form.get("action")

    try:
        app_logger.info(f"POST/ with action: {action} and URL: {url}")

        if not await is_valid_youtube_url(url):
            return await index(request, message=("danger", "Некорректная YouTube ссылка"))

        match action:
            case "download":
                return RedirectResponse(url=f"/download?url={url}")

            case "long_play":
                return templates.TemplateResponse(
                    "index.html",
                    {
                        "request": request,
                        "title": "Главная страница",
                        "video_url": f"/long_play?url={url}"
                    }
                )

            # case "fast_play":
            #     return RedirectResponse(url=f"/fast_play?url={url}")

            case _:
                return await index(request, message=("info", "Вы что-то жмакнули, я не понимаю"))

    except Exception as e:
        # todo возврат ошибки
        return 500
