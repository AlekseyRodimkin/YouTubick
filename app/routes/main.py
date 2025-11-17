from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse
from fastapi.responses import FileResponse

from app.services import exception_handler, is_valid_youtube_url

from ..config import crypto_addresses, templates

main_router = APIRouter(prefix="", tags=["main"])


@main_router.get("/", status_code=200, response_class=HTMLResponse)
@exception_handler()
async def index(request: Request) -> HTMLResponse:
    """Эндпоинт главной страницы"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@main_router.get("/support/help", status_code=200, response_class=HTMLResponse)
@exception_handler()
async def help_me(request: Request) -> HTMLResponse:
    """Эндпоинт страницы помощи"""
    return templates.TemplateResponse(
        "help_support.html", {"request": request, "crypto_addresses": crypto_addresses}
    )


@main_router.get("/validate_url", status_code=200, response_class=JSONResponse)
async def validate_url(url: str) -> dict:
    """Эндпоинт валидации url"""
    if not await is_valid_youtube_url(url=url):
        raise HTTPException(status_code=400, detail="Некорректная ссылка")

    return {"status": "ok"}


@main_router.get("/robots.txt")
async def robots_txt():
    return FileResponse("robots.txt")