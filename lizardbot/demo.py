from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes, RenderConfig
from hammett.core.screen import Screen
from hammett.core.mixins import StartMixin
from hammett.core.handlers import register_typing_handler
from hammett.core.handlers import register_button_handler
from disk import get_filenames, service, form_schedule


class HelloScreen(StartMixin, Screen):
    description = "Привет, это бот который собирает расписание, выбери дату."

    @register_button_handler
    async def get_date(self, update, context):
        payload = await self.get_payload(update, context)
        group = GetGroup(payload=payload)
        await group.jump(update, context)

    async def add_default_keyboard(self, update, _context):
        files = get_filenames()
        file_keyboard = []
        for file in files:
            button = Button(
                f'{file["name"]}'.replace('.xlsx', ''),
                self.get_date,
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
                payload=file["name"].replace('.xlsx', ''),
            )
            file_keyboard.append([button])

        return file_keyboard


class GetGroup(StartMixin, Screen):
    description = "Пришлите номер группы!"

    def __init__(self, payload=None, **kwargs):
        self.date = payload
        super().__init__()

    @register_typing_handler
    async def get_schedule(self, update, context):
        msg = update.message.text
        schedule = service(self.date, msg)
        if isinstance(schedule, str):
            rasp = GetSchedule()
            rasp.description = schedule
            await rasp.jump(update, context)
        else:
            schedule2 = f'{msg}\n' + ''.join(schedule).replace(',', '\n')
            schedule3 = form_schedule(schedule2)
            rasp = GetSchedule()
            rasp.description = schedule3
            await rasp.jump(update, context)


class GetSchedule(StartMixin, Screen):
    async def shedule_text(self):
        txt = "привет)"


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
