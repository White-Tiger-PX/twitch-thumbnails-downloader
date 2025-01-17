import sqlite3
import requests


def get_twitch_user_id(database_path, user_name, headers, main_logger):
    """
    Получает user_id из базы данных или из API, если его нет в базе данных.
    """
    try:
        logger = main_logger.getChild('get_twitch_user_id')
        correct_user_name = user_name.lower()
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_id
            FROM twitch_user_name_to_id_mapping
            WHERE user_name = ?
        ''', (correct_user_name,))

        result = cursor.fetchone()

        if result:
            return result[0]  # Возвращаем найденный user_id

        # Если ID не найден в базе данных, запрашиваем его с Twitch API
        url_user_id = f"https://api.twitch.tv/helix/users?login={correct_user_name}"
        response = requests.get(url_user_id, headers=headers, timeout=15)
        response.raise_for_status()
        user_data = response.json().get("data", [])

        if not user_data:
            return None

        user_id = user_data[0].get("id")

        cursor.execute('''
            INSERT OR REPLACE INTO twitch_user_name_to_id_mapping
            (user_name, user_id)
            VALUES (?, ?)
        ''', (correct_user_name, user_id))

        conn.commit()

        return user_id
    except requests.exceptions.RequestException as err:
        logger.error(f"Ошибка при получении ID для пользователя {correct_user_name}: {err}")

        return None
    except Exception as err:
        logger.error(f"Ошибка при работе с базой данных для пользователя {correct_user_name}: {err}")

        return None
    finally:
        cursor.close()
        conn.close()
