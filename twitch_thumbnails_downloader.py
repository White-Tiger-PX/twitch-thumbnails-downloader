import os
import time
import requests

import config

from set_logger import set_logger
from save_thumbnail import save_thumbnail
from fetch_access_token import fetch_access_token
from utils import get_created_at_local, create_file_path


def get_thumbnail_path(video_data):
    user_folder_path = os.path.join(config.folder_path, video_data['user_name'])

    os.makedirs(user_folder_path, exist_ok=True)

    datetime_at_local = get_created_at_local(video_data['created_at'], logger)
    date_created = datetime_at_local.date()
    name_components = [date_created, video_data['id'], 'thumbnail', video_data['user_name'], video_data['user_id']]

    thumbnail_save_path = create_file_path(
        folder_path=user_folder_path,
        name_components=name_components,
        extension='jpg',
        logger=logger
    )

    return thumbnail_save_path


def fetch_videos_and_update_thumbnails(user_id, headers):
    """Получает данные о последних видео пользователя и обновляет их обложки."""
    try:
        # Формируем URL с учетом параметра max_videos из конфига
        url_videos = f"https://api.twitch.tv/helix/videos?user_id={user_id}&sort=time"
        url_videos += f"&first={config.max_videos}"

        response_videos = requests.get(url_videos, headers=headers, timeout=15)
        response_videos.raise_for_status()
        videos_data = response_videos.json().get("data", [])

        for video_data in videos_data:
            thumbnail_url = video_data.get('thumbnail_url', None)

            if thumbnail_url:
                thumbnail_save_path = get_thumbnail_path(video_data)

                save_thumbnail(thumbnail_url, video_data, thumbnail_save_path, logger)
    except Exception as err:
        logger.error(f"Ошибка при получении данных о видео пользователя [ {user_id} ]: {err}")


def main():
    logger.info("Программа для скачивания обложек VOD-ов с Twitch запущена!")

    client_id = config.client_id
    client_secret = config.client_secret

    access_token = fetch_access_token(client_id, client_secret, logger)
    headers = {"Client-ID": client_id, "Authorization": "Bearer " + access_token}

    user_ids = config.user_ids

    for user_id in user_ids:
        try:
            fetch_videos_and_update_thumbnails(user_id, headers)
        except Exception as err:
            logger.error(f"Ошибка при обработке видео пользователя [ {user_id} ]: {err}")

        time.sleep(1)  # Соответствуем политике использования API


if __name__ == "__main__":
    logger = set_logger(log_folder=config.log_folder)

    main()
