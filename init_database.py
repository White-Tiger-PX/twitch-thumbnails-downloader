import sqlite3

import config

from set_logger import set_logger


def init_database(database_path, main_logger):
    try:
        logger = main_logger.getChild('init_database')
        logger.info("Инициализация базы данных.")

        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS twitch_user_name_to_id_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT UNIQUE,
                user_id TEXT
            )
        ''')

        conn.commit()
        logger.info("Инициализация базы данных завершена.")
    except Exception as err:
        logger.error("Ошибка при инициализации базы данных: %s", err)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    logger = set_logger(config.log_folder)

    init_database(
        database_path=config.database_path,
        main_logger=logger
    )
