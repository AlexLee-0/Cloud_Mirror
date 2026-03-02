import sys
import time
import logging
from utils.config_reader import load_config
from utils.logger import setup_logger
from core.cloud_storage import YandexDisk
from core.sync import sync_folders


def main():
    # Базовая настройка до чтения конфига
    logging.basicConfig(
        level=logging.INFO,
        format='%(name)s %(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Читаем конфиг
    settings = load_config('config.ini')

    # Настраиваем логгер
    logger = setup_logger(settings['log_file'])
    logger.info(f"Программа синхронизации файлов начинает работу с директорией {settings['local_folder']}")

    # Подключаемся к Яндекс.Диску и проверяем токен и папку
    try:
        yandex = YandexDisk(settings['token'], settings['cloud_folder'])
    except (ValueError, ConnectionError) as e:
        logger.error(e)
        sys.exit(1)

    if not yandex.ensure_folder_exists():
        logger.error(f"Папка '{settings['cloud_folder']}' не найдена в облаке")
        sys.exit(1)

    # Первичная синхронизация при запуске
    logger.info("Выполняется первичная синхронизация директории...")
    sync_folders(yandex, settings['local_folder'], settings['log_file'], logger)

    # Основной цикл синхронизации
    while True:
        time.sleep(settings['sync_interval'])
        sync_folders(yandex, settings['local_folder'], settings['log_file'], logger)


if __name__ == '__main__':
    main()