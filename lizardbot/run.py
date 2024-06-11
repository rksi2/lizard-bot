"""Модуль для запуска бота."""

from hammett.core import Application
from hammett.core.constants import DEFAULT_STATE

from lizardbot import WAITING_FOR_EDUCATOR_LAST_NAME, WAITING_FOR_GROUP_NAME
from lizardbot.screens import FullEducatorName, GetGroup, GetSchedule, StartScreen


def main() -> None:
    """Главная функция для запуска приложения."""
    name = 'Lizard_bot'
    app = Application(
        name,
        entry_point=StartScreen,
        states={
            DEFAULT_STATE: {GetSchedule, FullEducatorName},
            WAITING_FOR_GROUP_NAME: {GetGroup, StartScreen},
            WAITING_FOR_EDUCATOR_LAST_NAME: {StartScreen, FullEducatorName}
        },
    )
    app.run()


if __name__ == '__main__':
    main()
