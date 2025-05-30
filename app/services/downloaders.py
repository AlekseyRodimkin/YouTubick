import os

import yt_dlp

from config import logger

app_logger = logger.bind(name="app")
UPLOAD_DIR = "/uploads"


def download_video(url: str, filename: str, output_dir=UPLOAD_DIR):
    """Скачивает видео, возвращает имя готового файла"""
    try:
        app_logger.info(f"download_video({url})")

        output_template = os.path.join(output_dir, f"{filename}.%(ext)s")
        ydl_opts = {
            "format": "bestvideo[height<=1080][vcodec^=avc1]+bestaudio/best[height<=1080][vcodec^=avc1]",
            # 'format': 'bestvideo[vcodec^=avc1]+bestaudio/best[vcodec^=avc1]',
            "merge_output_format": "mp4",
            "outtmpl": output_template,
            "noplaylist": True,
            "postprocessor_args": ["-movflags", "+faststart"],
            "quiet": False,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp4"

            if os.path.exists(filename):
                app_logger.debug(f"Видео сохранено: {url}")
                return filename
    except Exception as e:
        app_logger.exception(f"Download error: {e}")
        raise Exception(f"Download error: {e}")
