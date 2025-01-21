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
