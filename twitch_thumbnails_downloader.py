import os
import time
import requests

import config

from set_logger import set_logger
from init_database import init_database
from save_thumbnail import save_thumbnail
from fetch_access_token import fetch_access_token
from get_twitch_user_id import get_twitch_user_id
from create_path import create_path


def fetch_videos_and_update_thumbnails(user_id, headers):
    """Получает данные о последних видео пользователя и обновляет их обложки."""
    try:
        # Формируем URL с учетом параметра videos_count из конфига
        url_videos = f"https://api.twitch.tv/helix/videos?user_id={user_id}&sort=time"

        # Если в конфиге указано значение для количества видео
        if config.max_videos is not None:
            url_videos += f"&first={config.max_videos}"

        response_videos = requests.get(url_videos, headers=headers, timeout=15)
        response_videos.raise_for_status()
        videos_data = response_videos.json().get("data", [])

        for video_data in videos_data:
            thumbnail_url = video_data.get('thumbnail_url', None)

            if thumbnail_url:
                user_folder_path = os.path.join(config.folder_path, video_data['user_name'])
                thumbnail_save_path = create_path(
                    video_data,
                    folder_path=user_folder_path,
                    prefix='thumbnail',
                    extension='jpg',
                    logger=logger
                )

                os.makedirs(user_folder_path, exist_ok=True)

                save_thumbnail(thumbnail_url, video_data, thumbnail_save_path, logger)
    except Exception as err:
        logger.error(f"Ошибка при получении данных о видео пользователя {user_id}: {err}")


def update_user_videos_thumbnails(headers, user_name):
    try:
        user_id = get_twitch_user_id(
            database_path=config.database_path,
            user_name=user_name,
            headers=headers,
            main_logger=logger
        )

        if user_id:
            logger.info(f"Обработка видео пользователя {user_name} (ID: {user_id})...")
            fetch_videos_and_update_thumbnails(user_id, headers)
        else:
            logger.error(f"Не удалось получить ID для пользователя {user_name}.")
    except Exception as err:
        logger.error(f"Ошибка при обработке видео пользователя {user_name}: {err}")


def main():
    logger.info("Программа для обновления обложек видео запущена!")

    init_database(
        database_path=config.database_path,
        main_logger=logger
    )

    client_id = config.client_id
    client_secret = config.client_secret

    access_token = fetch_access_token(client_id, client_secret, logger)
    headers = {"Client-ID": client_id, "Authorization": "Bearer " + access_token}

    user_names = config.user_names

    for user_name in user_names:
        update_user_videos_thumbnails(headers, user_name)
        time.sleep(1)  # Соответствуем политике использования API


if __name__ == "__main__":
    logger = set_logger(log_folder=config.log_folder)

    main()
