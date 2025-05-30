from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from app.services import exception_handler, is_valid_youtube_url
from config import crypto_addresses, logger, templates

main_router = APIRouter(prefix="", tags=["main"])
app_logger = logger.bind(name="app")


@main_router.get("/", status_code=200, response_class=HTMLResponse)
@exception_handler()
async def index(request: Request) -> HTMLResponse:
    """Эндпоинт главной страницы"""
    app_logger.info("GET/")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": " Главная страница",
        },
    )


@main_router.get("/support/help", status_code=200, response_class=HTMLResponse)
@exception_handler()
async def help_me(request: Request) -> HTMLResponse:
    """Эндпоинт страницы помощи"""
    app_logger.info("/support/help")

    return templates.TemplateResponse(
        "help_support.html", {"request": request, "crypto_addresses": crypto_addresses}
    )


@main_router.get("/validate_url", status_code=200, response_class=JSONResponse)
async def validate_url(url: str) -> dict:
    """Эндпоинт валидации url"""
    app_logger.info(f"/validate_url/{url}")

    if not await is_valid_youtube_url(url=url):
        raise HTTPException(status_code=400, detail="Некорректная ссылка")

    return {"status": "ok"}
