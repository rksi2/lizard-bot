"""Модуль с логикой бота и взаимодействием с API.

Содержит необходимые импорты для корректной работы.
"""

from typing import TYPE_CHECKING

from hammett.core import Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.handlers import register_typing_handler
from hammett.core.mixins import RouteMixin, StartMixin
from hammett.core.screen import RenderConfig, Screen

from lizardbot import WAITING_FOR_EDUCATOR_LAST_NAME, WAITING_FOR_GROUP_NAME
from lizardbot.client import API_CLIENT

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


class FullEducatorName(BaseScreen, RouteMixin):
    """Экран для ввода ФИО преподавателя."""

    routes = (
        ({DEFAULT_STATE, WAITING_FOR_EDUCATOR_LAST_NAME}, WAITING_FOR_EDUCATOR_LAST_NAME),
    )

    async def sjump(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Переопределения метода для настройки конфига."""
        config = kwargs.get('config', None)

        if config is None:
            config = await self.get_config(update, context, **kwargs)

        config.as_new_message = True
        await self.render(update, context, config=config)

        return await self._get_return_state_from_routes(
            update, context, self.routes,
        )

    @register_typing_handler
    async def process_educator_last_name(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Обрабатывает запрос на ФИО преподавателя."""
        message = update.message
        fio = message.text
        if fio.lower().startswith('фио'):
            last_name = fio.split()
            result = await API_CLIENT.get_fio_details(params={'fio': last_name[1]})

            return await FullEducatorName().sjump(
                update, context,
                config=RenderConfig(description=result),
            )

        return await self._get_return_state_from_routes(update, context, self.routes)

    async def add_default_keyboard(
        self: 'Self',
        _update: 'Update | None',
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


class GetGroup(BaseScreen, RouteMixin):
    """Экран для ввода номера группы пользователем."""

    description = 'Пришлите номер группы или фамилию преподавателя!'
    routes = (
        ({DEFAULT_STATE, WAITING_FOR_EDUCATOR_LAST_NAME}, WAITING_FOR_GROUP_NAME),
    )

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
        """Получение расписания группы."""
        message = update.message
        if message is None:
            return DEFAULT_STATE

        if message.text.lower().startswith('фио'):
            fio = message.text.split()
            result = await API_CLIENT.get_fio_details(params={'fio': fio[1]})

            return await FullEducatorName().sjump(
                update, context,
                config=RenderConfig(description=result),
            )

        """Обрабатывает ввод номера группы и получает расписание."""
        payload = context.user_data['payload']
        msg = message.text
        data = {'date': payload, 'group': msg}
        if any(char.isdigit() for char in msg):
            schedule = await API_CLIENT.get_service(params=data)

            return await GetSchedule().sjump(
                update, context,
                config=RenderConfig(description=schedule),
            )

        schedule = await API_CLIENT.get_teachers(params=data)

        return await GetSchedule().sjump(
            update, context,
            config=RenderConfig(description=schedule),
        )


class GetSchedule(BaseScreen, RouteMixin):
    """Экран для отображения расписания."""

    routes = (
        ({DEFAULT_STATE, WAITING_FOR_EDUCATOR_LAST_NAME}, WAITING_FOR_GROUP_NAME),
    )

    async def sjump(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Переопределение метода jump для настройки конфига."""
        config = kwargs.get('config', None)

        if config is None:
            config = await self.get_config(update, context, **kwargs)

        config.as_new_message = True
        await self.render(update, context, config=config)

        return await self._get_return_state_from_routes(
            update, context, self.routes,
        )

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
