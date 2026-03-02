import logging
import requests


class YandexDisk:
    """Класс для работы с Яндекс.Диском"""

    def __init__(self, token: str, cloud_folder: str):
        self.cloud_folder = cloud_folder
        self.base_url = 'https://cloud-api.yandex.net/v1/disk'
        self.headers = {'Authorization': f'OAuth {token}'}
        self.validate_token()

    def validate_token(self):
        """Проверяет токен при инициализации. Выбрасывает исключение если токен неверный."""
        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 401:
                raise ValueError("Неверный токен Яндекс.Диска")
            response.raise_for_status()
            logging.getLogger('CloudMirror').info("Токен Яндекс.Диска успешно проверен")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Не удалось подключиться к Яндекс.Диску: {e}")

    def get_info(self) -> dict:
        """Возвращает словарь {имя_файла: md5} для файлов в облачной папке."""
        try:
            response = requests.get(
                f'{self.base_url}/resources',
                headers=self.headers,
                params={'path': self.cloud_folder}
            )
            response.raise_for_status()
            items = response.json()['_embedded']['items']
            return {item['name']: item['md5'] for item in items if item['type'] == 'file'}

        except requests.exceptions.RequestException as e:
            logging.getLogger('CloudMirror').error(f"Ошибка при получении списка файлов: {e}")
            return {}

    def load(self, filepath: str, filename: str):
        """Загружает новый файл в облачное хранилище."""
        try:
            upload_url = self._get_upload_url(filename, overwrite=False)
            with open(filepath, 'rb') as f:
                requests.put(upload_url, files={'file': f})
            logging.getLogger('CloudMirror').info(f"Файл {filename} успешно записан.")

        except requests.exceptions.RequestException as e:
            logging.getLogger('CloudMirror').error(f"Файл {filename} не записан. {e}")

    def reload(self, filepath: str, filename: str):
        """Перезаписывает существующий файл в облачном хранилище."""
        try:
            upload_url = self._get_upload_url(filename, overwrite=True)
            with open(filepath, 'rb') as f:
                requests.put(upload_url, files={'file': f})
            logging.getLogger('CloudMirror').info(f"Файл {filename} успешно перезаписан.")

        except requests.exceptions.RequestException as e:
            logging.getLogger('CloudMirror').error(f"Файл {filename} не перезаписан. {e}")

    def delete(self, filename: str):
        """Удаляет файл из облачного хранилища."""
        try:
            requests.delete(
                f'{self.base_url}/resources',
                headers=self.headers,
                params={
                    'path': f'{self.cloud_folder}/{filename}',
                    'permanently': True
                }
            )
            logging.getLogger('CloudMirror').info(f"Файл {filename} успешно удалён.")

        except requests.exceptions.RequestException as e:
            logging.getLogger('CloudMirror').error(f"Файл {filename} не удалён. {e}")

    def ensure_folder_exists(self) -> bool:
        """Проверяет существование папки в облаке. Возвращает True если папка существует."""
        try:
            response = requests.get(
                f'{self.base_url}/resources',
                headers=self.headers,
                params={'path': self.cloud_folder}
            )
            return response.status_code == 200

        except requests.exceptions.RequestException:
            return False

    def _get_upload_url(self, filename: str, overwrite: bool) -> str:
        """Получает URL для загрузки файла."""
        response = requests.get(
            f'{self.base_url}/resources/upload',
            headers=self.headers,
            params={
                'path': f'{self.cloud_folder}/{filename}',
                'overwrite': overwrite
            }
        )
        response.raise_for_status()
        return response.json()['href']