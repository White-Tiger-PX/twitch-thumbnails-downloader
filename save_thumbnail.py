import os
import time
import requests

from datetime import datetime


def save_thumbnail(thumbnail_url, video_data, thumbnail_save_path, logger):
    try:
        thumbnail_url = thumbnail_url.replace("%{width}", "1920").replace("%{height}", "1080")
        response = requests.get(thumbnail_url, stream=True, timeout=10)

        if response.status_code != 200:
            error_message = response.text  # Получаем текст ответа для пояснения
            logger.error(
                f"Не удалось загрузить обложку (HTTP {response.status_code}). "
                f"Причина: {error_message}"
            )

            return

        video_log_info = f"[ {video_data['user_name']} - {video_data['id']} ]"

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
