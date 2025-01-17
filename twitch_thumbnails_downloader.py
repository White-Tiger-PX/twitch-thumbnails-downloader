import os
import time
import requests

from datetime import datetime, timedelta

import config

from set_logger import set_logger
from init_database import init_database
from fetch_access_token import fetch_access_token
from get_twitch_user_id import get_twitch_user_id


class CustomError(Exception):
    pass


def get_created_at_local(created_at):
    try:
        created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        created_at_local = created_at + timedelta(hours=config.utc_offset_hours)

        return created_at_local
    except ValueError as err:
        logger.error(f"Ошибка преобразования даты: {err}")

        raise CustomError("Ошибка в формате даты.")


def create_path(video_data, folder_path, prefix, extension='jpg'):
    try:
        datetime_at_local = get_created_at_local(video_data['created_at'])
        date_created = datetime_at_local.date()

        raw_filename = f"{date_created} - {video_data['id']} - {prefix} - {video_data['user_name']}.{extension}"
        sanitized_filename = "".join(x for x in raw_filename if x.isalnum() or x in [" ", "-", "_", "."])
        file_path = os.path.join(folder_path, sanitized_filename)

        return os.path.normpath(file_path)
    except KeyError as err:
        raise CustomError(f"Ошибка: отсутствует ключ {err} в данных видео.")
    except Exception as err:
        raise Exception(f"Ошибка при создании пути к видео: {err}")


def save_thumbnail(thumbnail_url, video_data, video_log_info):
    try:
        user_folder_path = os.path.join(config.folder_path, video_data['user_name'])
        thumbnail_save_path = create_path(
            video_data,
            folder_path=user_folder_path,
            prefix='thumbnail',
            extension='jpg'
        )

        os.makedirs(user_folder_path, exist_ok=True)

        thumbnail_url = thumbnail_url.replace("%{width}", "1920").replace("%{height}", "1080")
        response = requests.get(thumbnail_url, stream=True, timeout=10)

        if response.status_code != 200:
            error_message = response.text  # Получаем текст ответа для пояснения
            logger.error(
                f"Не удалось загрузить обложку (HTTP {response.status_code}). "
                f"Причина: {error_message}"
            )

            return

        if os.path.exists(thumbnail_save_path):
            existing_file_mod_time = datetime.fromtimestamp(os.path.getmtime(thumbnail_save_path))

            # Получаем время последней модификации на сервере из заголовков ответа (если доступно)
            remote_last_modified = response.headers.get('Last-Modified')

            if remote_last_modified:
                remote_last_modified = datetime.strptime(remote_last_modified, '%a, %d %b %Y %H:%M:%S GMT')

                # Заменяем файл только если локальная версия устарела
                if existing_file_mod_time >= remote_last_modified:
                    logger.info(f"Обложка для видео {video_log_info} уже актуальна.")

                    return

        with open(thumbnail_save_path, 'wb') as file:
            file.write(response.content)

        time.sleep(1)  # Соответствуем политике использования API

        logger.info(f"Обложка для видео {video_log_info} сохранена.")
    except Exception as err:
        logger.error(f"Ошибка при сохранении обложки для видео {video_log_info}: {err}")


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
            video_log_info = f"[ {video_data['user_name']} - {video_data['id']} ]"
            thumbnail_url = video_data.get('thumbnail_url', None)

            if thumbnail_url:
                save_thumbnail(thumbnail_url, video_data, video_log_info)
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
