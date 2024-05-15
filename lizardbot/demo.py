from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.screen import Screen
from hammett.core.mixins import StartMixin
from hammett.core.handlers import register_typing_handler


class HelloScreen(StartMixin, Screen):
    description = "Привет, это бот который собирает расписание, выбери дату."

    async def add_default_keyboard(self,_update,_context):
        return[[
            Button(
                '15.04',
                GetGroup,
                source_type=SourcesTypes.JUMP_SOURCE_TYPE,
            ),
            Button(
                '16.04',
                GetGroup,
                source_type=SourcesTypes.JUMP_SOURCE_TYPE,
            )
        ]]


class GetGroup(StartMixin, Screen):
    description = "Пришлите номер группы!"

    @register_typing_handler
    async def get_number(self, update, _context):
        nmbr = update.message.text


def main():
    name = 'Start_Screen'
    app = Application(
        name,
        entry_point=HelloScreen,
        states={
            DEFAULT_STATE: [HelloScreen, GetGroup],
        },
    )
    app.run()


if __name__ == "__main__":
    main()
