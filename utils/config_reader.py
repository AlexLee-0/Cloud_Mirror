import configparser
import logging
import os
import sys


def load_config(config_file: str = 'config.ini') -> dict:
    """
    Загружает и проверяет конфигурацию из файла.
    Возвращает словарь с настройками или завершает программу при ошибке.
    """
    config = configparser.ConfigParser()

    if not config.read(config_file, encoding='utf-8'):
        logging.error(f"Файл конфигурации '{config_file}' не найден")
        sys.exit(1)

    if not config.has_section('Settings'):
        logging.error("В файле конфигурации отсутствует секция [Settings]")
        sys.exit(1)

    try:
        settings = {
            'local_folder': config.get('Settings', 'local_folder'),
            'cloud_folder': config.get('Settings', 'cloud_folder'),
            'token': config.get('Settings', 'token'),
            'sync_interval': config.getint('Settings', 'sync_interval'),
            'log_file': config.get('Settings', 'log_file', fallback='sync.log')
        }
    except (configparser.NoOptionError, ValueError) as e:
        logging.error(f"Ошибка в файле конфигурации: {e}")
        sys.exit(1)

    if not os.path.exists(settings['local_folder']):
        logging.error(f"Папка '{settings['local_folder']}' не существует")
        sys.exit(1)

    if not settings['token']:
        logging.error("Токен доступа не может быть пустым")
        sys.exit(1)

    if settings['sync_interval'] <= 0:
        logging.error("Период синхронизации должен быть положительным числом")
        sys.exit(1)

    log_dir = os.path.dirname(settings['log_file'])
    if log_dir and not os.path.exists(log_dir):
        logging.error(f"Директория для лога '{log_dir}' не существует")
        sys.exit(1)

    return settings