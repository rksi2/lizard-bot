from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes, RenderConfig
from hammett.core.screen import Screen
from hammett.core.mixins import StartMixin
from hammett.core.handlers import register_typing_handler
from hammett.core.handlers import register_button_handler
from disk import get_filenames, service, form_schedule


class BaseScreen(Screen):
    hide_keyboard = True


class StartScreen(StartMixin, BaseScreen):
    description = 'Привет, это бот который собирает расписание, выбери дату.'

    async def add_default_keyboard(self, update, _context):
        files = get_filenames()
        file_keyboard = []
        for file in files:
            button = Button(
                f'{file["name"]}'.replace('.xlsx', ''),
                GetGroup,
                source_type=SourcesTypes.GOTO_SOURCE_TYPE,
                payload=file["name"].replace('.xlsx', ''),

            )
            file_keyboard.append([button])

        return file_keyboard


class GetGroup(BaseScreen):
    description = "Пришлите номер группы!"

    async def goto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        payload = await self.get_payload(update, context)
        context.user_data['payload'] = payload
        print(payload)
        return await super().jump(update, context, **kwargs)

    @register_typing_handler
    async def get_schedule(self, update, context):
        payload = context.user_data.get('payload')
        msg = update.message.text
        schedule = service(payload, msg)
        if isinstance(schedule, str):
            rasp = GetSchedule()
            rasp.description = schedule
            await rasp.jump(update, context)
        else:
            schedule2 = f'{msg.upper()}\n' + ''.join(schedule).replace(',', '\n')
            schedule3 = form_schedule(schedule2)
            rasp = GetSchedule()
            rasp.description = schedule3
            await rasp.jump(update, context)


class GetSchedule(BaseScreen):
    async def add_default_keyboard(self, update, context):
        return [
            [
                Button(
                    "Вернуться к выбору даты",
                    source=StartScreen,
                    source_type=SourcesTypes.GOTO_SOURCE_TYPE
                )
            ]
        ]


def main():
    name = 'Start_Screen'
    app = Application(
        name,
        entry_point=StartScreen,
        states={
            DEFAULT_STATE: [StartScreen, GetGroup, GetSchedule],
        },
    )
    app.run()


if __name__ == "__main__":
    main()
