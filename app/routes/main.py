from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from app.services import is_valid_youtube_url, return_index_page, exception_handler, send_email_task
from config.logging_config import logger
from config.config import EMAIL_PASS_FOR_TEST_ENDPOINT, templates, crypto_addresses

main_router = APIRouter(prefix="", tags=["main"])
app_logger = logger.bind(name="app")


@main_router.get("/", status_code=200, response_class=HTMLResponse)
@exception_handler()
async def index(request: Request):
    app_logger.info(f"GET/")
    return await return_index_page(request=request)


@main_router.post("/")
@exception_handler()
async def post_index(request: Request):
    form = await request.form()
    url = form.get("url")
    action = form.get("action")

    app_logger.info(f"POST/?action={action}&url={url}")

    if not await is_valid_youtube_url(url):
        return await return_index_page(request=request, message=("danger", "Некорректная YouTube ссылка"))
    #
    # match action:
    #     case "live_play":
    #         return await return_index_page(request=request, video_url=f"/fast_play?url={url}")
    #
    #     case "error":
    #         raise Exception("Скачивание завершилось ошибкой")
    #
    #     case _:
    #         return await return_index_page(request=request, message=("info", "Вы что-то жмакнули, я не понимаю"))


@main_router.get(f"/test-send-email/{EMAIL_PASS_FOR_TEST_ENDPOINT}")
@exception_handler()
async def test_mail_by_get(request: Request):
    env = Environment(loader=FileSystemLoader("/home/aleksei/PycharmProjects/youtube_video/app/static/templates"))
    template = env.get_template("test_mail.html")
    html_body = template.render()

    send_email_task.delay(
        subject="Test Email Celery Task",
        body=html_body
    )
    return {"status": "Email Celery задача запущена (через GET)"}


@main_router.get(f"/support/help")
@exception_handler()
async def help_me(request: Request):
    return templates.TemplateResponse(
        "support_help.html",
        {
            "request": request,
            "crypto_addresses": crypto_addresses
        }
    )
