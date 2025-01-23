import os

from datetime import datetime, timedelta

import config


def get_created_at_local(created_at, logger):
    try:
        created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        created_at_local = created_at + timedelta(hours=config.utc_offset_hours)

        return created_at_local
    except ValueError as err:
        logger.error(f"Ошибка преобразования даты: {err}")

        raise Exception("Ошибка в формате даты.")


def create_file_basename(name_components, extension, logger):
    try:
        name_components = [str(item) for item in name_components]
        raw_filename = f"{' - '.join(name_components)}.{extension}"
        sanitized_filename = "".join(
            char for char in raw_filename if char.isalnum() or char in [" ", "-", "_", "."]
        )

        return sanitized_filename
    except Exception as err:
        logger.error(f"Ошибка при создании имени файла: {err}")

        raise


def create_file_path(folder_path, name_components, extension, logger):
    try:
        basename = create_file_basename(name_components, extension, logger)
        file_path = os.path.join(folder_path, basename)

        return os.path.normpath(file_path)
    except Exception as err:
        logger.error(f"Ошибка при создании пути к файлу: {err}")

        raise


def get_thumbnail_path(video_data, logger):
    user_folder_path = os.path.join(config.folder_path, video_data['user_name'])

    os.makedirs(user_folder_path, exist_ok=True)

    datetime_at_local = get_created_at_local(video_data['created_at'], logger)
    date_created = datetime_at_local.date()

    name_components = [date_created, video_data['id'], 'thumbnail', video_data['user_name']]
    thumbnail_save_path = create_file_path(
        folder_path=user_folder_path,
        name_components=name_components,
        extension='jpg',
        logger=logger
    )

    return thumbnail_save_path
