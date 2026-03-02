import os
import hashlib
import logging


def get_local_files(local_folder: str, log_file: str) -> dict:
    """Возвращает словарь {имя_файла: полный_путь} для локальной папки.
    Исключает файл лога если он находится в папке синхронизации."""
    log_file_normalized = os.path.normpath(log_file)
    result = {}
    for filename in os.listdir(local_folder):
        filepath = os.path.join(local_folder, filename)
        filepath_normalized = os.path.normpath(filepath)
        if os.path.isfile(filepath) and filepath_normalized != log_file_normalized:
            result[filename] = filepath
    return result


def get_local_md5(filepath: str) -> str:
    """Вычисляет md5 хэш локального файла."""
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def upload_new_files(yandex, local_files: dict, cloud_files: dict):
    """Загружает файлы которые есть локально, но нет в облаке."""
    for filename, filepath in local_files.items():
        if filename not in cloud_files:
            yandex.load(filepath, filename)


def update_changed_files(yandex, local_files: dict, cloud_files: dict):
    """Перезаписывает файлы у которых отличается md5."""
    for filename, filepath in local_files.items():
        if filename in cloud_files:
            local_md5 = get_local_md5(filepath)
            if local_md5 != cloud_files[filename]:
                yandex.reload(filepath, filename)


def delete_removed_files(yandex, local_files: dict, cloud_files: dict):
    """Удаляет из облака файлы которых нет локально."""
    for filename in cloud_files:
        if filename not in local_files:
            yandex.delete(filename)


def sync_folders(yandex, local_folder: str, log_file: str, logger: logging.Logger):
    """Основная функция синхронизации — вызывается из main.py."""
    try:
        local_files = get_local_files(local_folder, log_file)
        cloud_files = yandex.get_info()

        upload_new_files(yandex, local_files, cloud_files)
        update_changed_files(yandex, local_files, cloud_files)
        delete_removed_files(yandex, local_files, cloud_files)

    except Exception as e:
        logger.error(f"Ошибка при синхронизации: {e}")