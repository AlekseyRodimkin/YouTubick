from config import celery_app

from .downloaders import download_video
from .utils import generate_unique_string, send_mail
from config import logger

app_logger = logger.bind(name="app")


@celery_app.task(bind=True, max_retries=3)
def celery_task_download_video(self, url):
    """Задача скачивания видео"""
    try:
        unique_name = generate_unique_string(prefix="your_video__")
        filename = download_video(url=url, filename=unique_name)
        app_logger.info(f"[celery_task_download_video] Скачано: {filename}")
        return {"status": "success", "filename": filename}
    except Exception as e:
        app_logger.exception(f"[celery_task_download_video] Ошибка: {e}")
        self.retry(exc=e, countdown=5)


@celery_app.task(bind=True, max_retries=3)
def celery_task_send_email(self, subject, body, to_email):
    """Задача отправки email"""
    try:
        send_mail(subject=subject, body=body, to_email=to_email)
        app_logger.info(f"[celery_task_send_email] : Отправлено: {subject}")
    except Exception as e:
        app_logger.exception(f"[celery_task_send_email] Ошибка: {e}")
        self.retry(exc=e, countdown=5)
