"""Модуль для запуска бота."""

from hammett.core import Application
from hammett.core.constants import DEFAULT_STATE

from lizardbot import WAITING_FOR_GROUP_NAME
from lizardbot.screens import GetGroup, GetSchedule, StartScreen


def main() -> None:
    """Главная функция для запуска приложения."""
    name = 'Lizard_bot'
    app = Application(
        name,
        entry_point=StartScreen,
        states={
            DEFAULT_STATE: {GetSchedule},
            WAITING_FOR_GROUP_NAME: {GetGroup, StartScreen},
        },
    )
    app.run()


if __name__ == '__main__':
    main()
