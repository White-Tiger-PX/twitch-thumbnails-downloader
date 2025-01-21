import os

from utils import get_created_at_local


def create_path(video_data, folder_path, prefix, extension, logger):
    try:
        datetime_at_local = get_created_at_local(video_data['created_at'], logger)
        date_created = datetime_at_local.date()

        raw_filename = f"{date_created} - {video_data['id']} - {prefix} - {video_data['user_name']}.{extension}"
        sanitized_filename = "".join(x for x in raw_filename if x.isalnum() or x in [" ", "-", "_", "."])
        file_path = os.path.join(folder_path, sanitized_filename)

        return os.path.normpath(file_path)
    except KeyError as err:
        raise Exception(f"Ошибка: отсутствует ключ {err} в данных видео.")
    except Exception as err:
        raise Exception(f"Ошибка при создании пути к видео: {err}")
