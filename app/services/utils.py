from urllib.parse import urlparse, parse_qs
import os
from config.logging_config import logger

app_logger = logger.bind(name="app")


async def is_valid_youtube_url(url: str) -> bool:
    """Проверяет, является ли youtube ссылка валидной"""
    try:
        app_logger.info(f"is_valid_youtube_url({url})")
        result = urlparse(url)

        if not all([result.scheme in ('http', 'https'), result.netloc]):
            return False

        if not any(domain in result.netloc for domain in ['youtube.com', 'youtu.be']):
            return False

        if 'youtube.com' in result.netloc:
            if 'watch' in result.path:
                query = parse_qs(result.query)
                return 'v' in query and len(query['v'][0]) == 11

            elif '/v/' in result.path:
                video_id = result.path.split('/v/')[1]
                return len(video_id) == 11

        elif 'youtu.be' in result.netloc:
            video_id = result.path[1:]
            return len(video_id) == 11

        elif 'embed' in result.path:
            video_id = result.path.split('/')[-1]
            return len(video_id) == 11

        return False

    except Exception:
        return False


def file_streamer(path: str, chunk_size: int = 1024 * 1024):
    """Передает файл, удаляет по завершению"""
    try:
        app_logger.info(f"file_streamer({path})")

        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                yield chunk
    finally:
        os.remove(path)
        app_logger.info(f"Файл удалён: {path}")


def delete_file(path: str):
    """Функция удаления файла"""
    try:
        os.remove(path)
        app_logger.info(f"Файл удалён после просмотра: {path}")
    except Exception as e:
        app_logger.error(f"Ошибка удаления файла: {e}")
