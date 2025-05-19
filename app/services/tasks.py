import smtplib
from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from config.config import celery_app, EMAIL_ADDRESS, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
from .downloaders import download_video
from .utils import generate_unique_string


@celery_app.task(bind=True, max_retries=3)
def celery_task_download_video(self, url):
    try:
        unique_name = generate_unique_string(prefix="your_video__")
        filename = download_video(url=url, filename=unique_name)
        return {"status": "success", "filename": filename}
    except Exception as e:
        self.retry(exc=e, countdown=5)


@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, subject: str, body: str, to_email: str = EMAIL_ADDRESS):
    try:
        pass
    except Exception as e:
        self.retry(exc=e, countdown=5)
