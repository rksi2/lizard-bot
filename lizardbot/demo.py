from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.screen import Screen
from hammett.core.mixins import StartMixin, RouteMixin
from hammett.core.handlers import register_typing_handler
from lizardbot import WAITING_FOR_GROUP_NAME
import requests


class BaseScreen(Screen):
    hide_keyboard = True


class StartScreen(StartMixin, BaseScreen):
    description = 'Привет, это бот который собирает расписание, выбери дату.'

    async def add_default_keyboard(self, update, _context):
        response = requests.get('http://127.0.0.1:8000/api/files')
        files = response.json()
        file_keyboard = []
        for file in files:
            button = Button(
                f'{file["name"]}'.replace('.xlsx', ''),
                GetGroup,
                source_type=SourcesTypes.SGOTO_SOURCE_TYPE,
                payload=file["name"].replace('.xlsx', ''),

            )
            file_keyboard.append([button])

        return file_keyboard


class GetGroup(BaseScreen, RouteMixin):
    description = "Пришлите номер группы!"
    routes = (
        ({DEFAULT_STATE}, WAITING_FOR_GROUP_NAME),
    )
    async def sgoto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        payload = await self.get_payload(update, context)
        context.user_data['payload'] = payload

        return await super().sgoto(update, context, **kwargs)

    @register_typing_handler
    async def get_schedule(self, update, context):
        payload = context.user_data.get('payload')
        msg = update.message.text
        data = {
            'date':payload,
            'group':msg
        }

        if any(char.isdigit() for char in msg):
            response = requests.post('http://127.0.0.1:8000/api/service/', json=data)
            if response.status_code != 200:
                print(f"Ошибка: статус код {response.status_code}")
            schedule = response.json()
            rasp = GetSchedule()
            rasp.description = schedule
            return await rasp.jump(update, context)
        response = requests.post('http://127.0.0.1:8000/api/teachers/', json=data)
        if response.status_code != 200:
            print(f"Ошибка: статус код {response.status_code}")
        schedule = response.json()
        rasp = GetSchedule()
        rasp.description = schedule
        return await rasp.jump(update, context)



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
            DEFAULT_STATE: {StartScreen,GetSchedule},
            WAITING_FOR_GROUP_NAME: {GetGroup},
        },
    )
    app.run()


if __name__ == "__main__":
    main()
