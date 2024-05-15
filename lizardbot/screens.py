"""Модуль с логикой бота и взаимодействием с API.

Содержит необходимые импорты для корректной работы.
"""

from typing import TYPE_CHECKING

from lizardbot.client import API_CLIENT
from hammett.core import Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.handlers import register_typing_handler
from hammett.core.mixins import RouteMixin, StartMixin
from hammett.core.screen import Screen

from lizardbot import WAITING_FOR_GROUP_NAME

if TYPE_CHECKING:
    from typing import Any, Self

    from hammett.types import Keyboard, State
    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD


class BaseScreen(Screen):
    """Базовый класс для всех экранов бота."""

    hide_keyboard = True


class StartScreen(StartMixin, BaseScreen):
    """Начальный экран бота, предоставляет список доступных расписаний."""

    description = 'Привет, это бот который собирает расписание, выбери дату.'

    async def add_default_keyboard(
        self: 'Self',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Keyboard':
        """Добавляет клавиатуру по умолчанию с доступными файлами расписаний."""
        files = await API_CLIENT.get_files()

        keyboard = []
        for file in files:
            button = Button(
                f'{file["name"]}'.replace('.xlsx', ''),
                GetGroup,
                source_type=SourcesTypes.SGOTO_SOURCE_TYPE,
                payload=file['name'].replace('.xlsx', ''),
            )
            keyboard.append([button])

        return keyboard


class GetGroup(BaseScreen, RouteMixin):
    """Экран для ввода номера группы пользователем."""

    description = 'Пришлите номер группы или фамилию преподавателя!'
    routes = (({DEFAULT_STATE}, WAITING_FOR_GROUP_NAME),)

    async def sgoto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Переход к экрану ввода номера группы."""
        payload = await self.get_payload(update, context)
        context.user_data['payload'] = payload

        return await super().sgoto(update, context, **kwargs)

    @register_typing_handler
    async def get_schedule(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Обрабатывает ввод номера группы и получает расписание."""
        payload = await self.get_payload(update, context)
        msg = update.message.text
        data = {'date': payload, 'group': msg}

        if any(char.isdigit() for char in msg):
            schedule = await API_CLIENT.get_service(params=data)

            rasp = GetSchedule()
            rasp.description = schedule
            await rasp.jump(update, context)

            return await self._get_return_state_from_routes(update, context, self.routes)

        schedule = await API_CLIENT.get_teachers(params=data)

        rasp = GetSchedule()
        rasp.description = schedule
        await rasp.jump(update, context)

        return await self._get_return_state_from_routes(update, context, self.routes)


class GetSchedule(BaseScreen):
    """Экран для отображения расписания."""

    async def add_default_keyboard(
        self: 'Self',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Keyboard':
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
