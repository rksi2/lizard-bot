from screens import StartScreen, GetSchedule, GetGroup
import logging
from typing import Any
import aiohttp
from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE
from lizardbot import WAITING_FOR_GROUP_NAME

def main() -> None:
    """Главная функция для запуска приложения."""
    name = "Lizard_bot"
    app = Application(
        name,
        entry_point=StartScreen,
        states={
            DEFAULT_STATE: {GetSchedule},
            WAITING_FOR_GROUP_NAME: {GetGroup, StartScreen},
        },
    )
    app.run()


if __name__ == "__main__":
    main()
