import psutil


def is_file_in_use_by_streamlink(file_path):
    """
    Проверяет, используется ли файл процессом streamlink.
    """
    for proc in psutil.process_iter(attrs=['name', 'cmdline']):
        try:
            if 'streamlink' in proc.info['name']:
                # Проверяем, указан ли файл в аргументах процесса
                if file_path in proc.info['cmdline']:
                    return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue

    return False  # Файл не используется процессом streamlink
