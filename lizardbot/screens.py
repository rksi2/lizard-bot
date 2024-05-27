from lizardbot import logger
from typing import Any
import aiohttp
from hammett.core import  Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.handlers import register_typing_handler
from hammett.core.mixins import RouteMixin, StartMixin
from hammett.core.screen import Screen
from hammett.types import BD, BT, CD, UD, CallbackContext, State, Update

from lizardbot import WAITING_FOR_GROUP_NAME

# Настройка логгера


TIMEOUT = 10
HTTP_OK = 200


class BaseScreen(Screen):
    """Базовый класс для всех экранов бота."""

    hide_keyboard = True


class StartScreen(StartMixin, BaseScreen):
    """Начальный экран бота, предоставляет список доступных расписаний."""

    description = "Привет, это бот который собирает расписание, выбери дату."

    async def add_default_keyboard(
            self: 'Self',
            _update: 'Update',
            _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Keyboard':
        """Добавляет клавиатуру по умолчанию с доступными файлами расписаний."""
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8000/api/files", timeout=TIMEOUT) as response:
                if response.status != HTTP_OK:
                    logger.error(f"Failed to fetch files: {response.status}")
                    return []
                if response.content_type != 'application/json':
                    logger.error(f"Unexpected content type: {response.content_type}")
                    return []
                files = await response.json()

        file_keyboard = []
        for file in files:
            button = Button(
                f'{file["name"]}'.replace(".xlsx", ""),
                GetGroup,
                source_type=SourcesTypes.SGOTO_SOURCE_TYPE,
                payload=file["name"].replace(".xlsx", ""),
            )
            file_keyboard.append([button])

        return file_keyboard


class GetGroup(BaseScreen, RouteMixin):
    """Экран для ввода номера группы пользователем."""

    description = "Пришлите номер группы!"
    routes = (
        ({DEFAULT_STATE}, WAITING_FOR_GROUP_NAME),
    )

    async def sgoto(
        self: "GetGroup",
        update: Update,
        context: CallbackContext[BT, UD, CD, BD],
        **kwargs: Any,
    ) -> State:
        """Переход к экрану ввода номера группы."""
        payload = await self.get_payload(update, context)
        context.user_data["payload"] = payload

        return await super().sgoto(update, context, **kwargs)

    @register_typing_handler
    async def get_schedule(self: "GetGroup", update: Update, context: CallbackContext[BT, UD, CD, BD]) -> State:
        """Обрабатывает ввод номера группы и получает расписание."""
        payload = context.user_data.get("payload")
        msg = update.message.text
        data = {"date": payload, "group": msg}

        async with aiohttp.ClientSession() as session:
            if any(char.isdigit() for char in msg):
                async with session.post("http://127.0.0.1:8000/api/service/", json=data, timeout=TIMEOUT) as response:
                    if response.status != HTTP_OK:
                        logger.error("Ошибка: статус код %d", response.status)
                    if response.content_type != 'application/json':
                        logger.error(f"Unexpected content type: {response.content_type}")
                        return await self._get_return_state_from_routes(update, context, self.routes)
                    schedule = await response.json()
                rasp = GetSchedule()
                rasp.description = schedule
                await rasp.jump(update, context)
                return await self._get_return_state_from_routes(update, context, self.routes)

            async with session.post("http://127.0.0.1:8000/api/teachers/", json=data, timeout=TIMEOUT) as response:
                if response.status != HTTP_OK:
                    logger.error("Ошибка: статус код %d", response.status)
                if response.content_type != 'application/json':
                    logger.error(f"Unexpected content type: {response.content_type}")
                    return await self._get_return_state_from_routes(update, context, self.routes)
                schedule = await response.json()

        rasp = GetSchedule()
        rasp.description = schedule
        await rasp.jump(update, context)
        return await self._get_return_state_from_routes(update, context, self.routes)


class GetSchedule(BaseScreen):
    """Экран для отображения расписания."""

    async def add_default_keyboard(
        self: "GetSchedule", _update: Update, _context: CallbackContext[BT, UD, CD, BD],
    ) -> list[list[Button]]:
        """Добавляет клавиатуру с кнопкой возврата к выбору даты."""
        return [
            [
                Button(
                    "Вернуться к выбору даты",
                    source=StartScreen,
                    source_type=SourcesTypes.SJUMP_SOURCE_TYPE,
                ),
            ],
        ]



