"""Модуль клиента для взаимодействия с API."""

from typing import TYPE_CHECKING, Any

import httpx
from hammett.conf import settings

from lizardbot import LOGGER

if TYPE_CHECKING:
    from typing import Self


class ApiClient:
    """HTTP клиент для взаимодействия с внешним API."""

    def __init__(self: 'Self') -> None:
        """Инициализация HTTP клиента."""
        self._client = httpx.AsyncClient(timeout=settings.TIMEOUT)

    @staticmethod
    def _build_url(endpoint: str) -> str:
        """Создает полный URL из базового API_URL и заданного endpoint."""
        return f'{settings.API_URL}{endpoint}'

    async def get_files(self: 'Self') -> 'httpx.Response':
        """Получает список файлов."""
        url = self._build_url('/api/files/')
        response = await self._client.get(url)
        if response.status_code != httpx.codes.OK:
            LOGGER.error(f'Failed to fetch files: {response.status_code}')

        return response.json()

    async def get_service(self: 'Self', params: dict[str, Any]) -> 'httpx.Response':
        """Получает информацию о сервисе."""
        url = self._build_url('/api/service/')
        response = await self._client.get(url, params=params)
        if response.status_code != httpx.codes.OK:
            LOGGER.error(f'Failed to fetch files: {response.status_code}')

        return response.json()

    async def get_teachers(self: 'Self', params: dict[str, Any]) -> 'httpx.Response':
        """Получает информацию о преподавателях."""
        url = self._build_url('/api/teachers/')
        response = await self._client.get(url, params=params)
        if response.status_code != httpx.codes.OK:
            LOGGER.error(f'Failed to fetch files: {response.status_code}')

        return response.json()


# Создаем единственный экземпляр клиента, который будет использоваться в приложении
API_CLIENT = ApiClient()
