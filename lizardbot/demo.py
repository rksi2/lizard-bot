"""
Файл построения логики бота и взаимодействия с API

Содержит необходимые импорты для работы приложения.
"""

# Модули Hammett.core Application и Button для работы API и кнопок
from hammett.core import Application, Button
# Модули Hammett.core для перехода между State
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
# Модуль Hammett.core.screen для работы с телеграмм сообщениями
from hammett.core.screen import Screen
# Модули Hammett.core.mixins для обработки команды /start и переключения между State
from hammett.core.mixins import StartMixin, RouteMixin
# Модуль hammett.core.handlers для регистрации и обработки сообщений пользователя
from hammett.core.handlers import register_typing_handler
# Модуль lizardbot который ожидает ввод имени
from lizardbot import WAITING_FOR_GROUP_NAME
# Библиотека для запросов в боте
import requests


class BaseScreen(Screen):
    """Базовый экран с скрытой клавиатурой."""

    hide_keyboard = True


class StartScreen(StartMixin, BaseScreen):
    """Начальный экран бота, предоставляет список доступных расписаний."""

    description = "Привет, это бот который собирает расписание, выбери дату."

    async def add_default_keyboard(self, update, _context) -> "List[List[Button]]":
        """Добавляет клавиатуру по умолчанию с доступными файлами расписаний."""

        response = requests.get("http://127.0.0.1:8000/api/files")
        files = response.json()
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
    routes = (({DEFAULT_STATE}, WAITING_FOR_GROUP_NAME),)

    async def sgoto(
        self: "Self",
        update: "Update",
        context: "CallbackContext[BT, UD, CD, BD]",
        **kwargs: "Any",
    ) -> "State":
        """Переход к экрану ввода номера группы."""

        payload = await self.get_payload(update, context)
        context.user_data["payload"] = payload

        return await super().sgoto(update, context, **kwargs)

    @register_typing_handler
    async def get_schedule(self, update, context) -> "State":
        """Обрабатывает ввод номера группы и получает расписание."""

        payload = context.user_data.get("payload")
        msg = update.message.text
        data = {"date": payload, "group": msg}

        if any(char.isdigit() for char in msg):
            response = requests.post("http://127.0.0.1:8000/api/service/", json=data)
            if response.status_code != 200:
                print(f"Ошибка: статус код {response.status_code}")
            schedule = response.json()
            rasp = GetSchedule()
            rasp.description = schedule
            return await rasp.jump(update, context)

        response = requests.post("http://127.0.0.1:8000/api/teachers/", json=data)
        if response.status_code != 200:
            print(f"Ошибка: статус код {response.status_code}")
        schedule = response.json()
        rasp = GetSchedule()
        rasp.description = schedule
        return await rasp.jump(update, context)


class GetSchedule(BaseScreen):
    """Экран для отображения расписания."""

    async def add_default_keyboard(self, update, context) -> "List[List[Button]]":
        """Добавляет клавиатуру с кнопкой возврата к выбору даты."""

        return [
            [
                Button(
                    "Вернуться к выбору даты",
                    source=StartScreen,
                    source_type=SourcesTypes.GOTO_SOURCE_TYPE,
                )
            ]
        ]


def main():
    """Главная функция для запуска приложения."""

    name = "Start_Screen"
    app = Application(
        name,
        entry_point=StartScreen,
        states={
            DEFAULT_STATE: {StartScreen, GetSchedule},
            WAITING_FOR_GROUP_NAME: {GetGroup},
        },
    )
    app.run()


if __name__ == "__main__":
    main()
