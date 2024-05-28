"""
Модуль screens.py с логикой бота и взаимодействием с API.

Содержит необходимые импорты для корректной работы.
"""

from typing import TYPE_CHECKING, Any

import httpx
from hammett.core import Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.handlers import register_typing_handler
from hammett.core.mixins import RouteMixin, StartMixin
from hammett.core.screen import Screen
from settings import API_HOST, API_PORT

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
from hammett.types import Keyboard, State

from lizardbot import LOGGER, WAITING_FOR_GROUP_NAME

TIMEOUT = 10
HTTP_OK = 200


class BaseScreen(Screen):
    """Базовый класс для всех экранов бота."""

    hide_keyboard = True


class StartScreen(StartMixin, BaseScreen):
    """Начальный экран бота, предоставляет список доступных расписаний."""

    description = 'Привет, это бот который собирает расписание, выбери дату.'

    async def add_default_keyboard(
        self: 'Any',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> Keyboard:
        """Добавляет клавиатуру по умолчанию с доступными файлами расписаний."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'http://{API_HOST}:{API_PORT}/api/files/',
                timeout=TIMEOUT,
            )
            if response.status_code != HTTP_OK:
                LOGGER.error(f'Failed to fetch files: {response.status_code}')

                return []

            if response.headers['content-type'] != 'application/json':
                LOGGER.error(f"Unexpected content type: {response.headers['content-type']}")

                return []

            files = response.json()

        file_keyboard = []
        for file in files:
            button = Button(
                f'{file["name"]}'.replace('.xlsx', ''),
                GetGroup,
                source_type=SourcesTypes.SGOTO_SOURCE_TYPE,
                payload=file['name'].replace('.xlsx', ''),
            )
            file_keyboard.append([button])

        return file_keyboard


class GetGroup(BaseScreen, RouteMixin):
    """Экран для ввода номера группы пользователем."""

    description = 'Пришлите номер группы или фамилию преподавателя!'
    routes = (({DEFAULT_STATE}, WAITING_FOR_GROUP_NAME),)

    async def sgoto(
        self: 'Any',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: Any,
    ) -> State:
        """Переход к экрану ввода номера группы."""
        payload = await self.get_payload(update, context)
        context.user_data['payload'] = payload

        return await super().sgoto(update, context, **kwargs)

    @register_typing_handler
    async def get_schedule(
        self: 'Any',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> State:
        """Обрабатывает ввод номера группы и получает расписание."""
        payload = context.user_data.get('payload')
        msg = update.message.text
        data = {'date': payload, 'group': msg}

        async with httpx.AsyncClient() as client:
            if any(char.isdigit() for char in msg):
                response = await client.post(
                    f'http://{API_HOST}:{API_PORT}/api/service/',
                    json=data,
                    timeout=TIMEOUT,
                )
                if response.status_code != HTTP_OK:
                    LOGGER.error('Ошибка: статус код %d', response.status_code)
                if response.headers['content-type'] != 'application/json':
                    LOGGER.error(f"Unexpected content type: {response.headers['content-type']}")

                    return await self._get_return_state_from_routes(
                        update,
                        context,
                        self.routes,
                    )

                schedule = response.json()
                rasp = GetSchedule()
                rasp.description = schedule
                await rasp.jump(update, context)

                return await self._get_return_state_from_routes(update, context, self.routes)

            response = await client.post(
                f'http://{API_HOST}:{API_PORT}/api/teachers/',
                json=data,
                timeout=TIMEOUT,
            )
            if response.status_code != HTTP_OK:
                LOGGER.error('Ошибка: статус код %d', response.status_code)
            if response.headers['content-type'] != 'application/json':
                LOGGER.error(f"Unexpected content type: {response.headers['content-type']}")

                return await self._get_return_state_from_routes(update, context, self.routes)

            schedule = response.json()

        rasp = GetSchedule()
        rasp.description = schedule
        await rasp.jump(update, context)

        return await self._get_return_state_from_routes(update, context, self.routes)


class GetSchedule(BaseScreen):
    """Экран для отображения расписания."""

    async def add_default_keyboard(
        self: 'Any',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> list[list[Button]]:
        """Добавляет клавиатуру с кнопкой возврата к выбору даты."""

        return [
            [
                Button(
                    'Вернуться к выбору даты',
                    source=StartScreen,
                    source_type=SourcesTypes.JUMP_SOURCE_TYPE,
                ),
            ],
        ]
