from google.oauth2 import service_account
from googleapiclient.discovery import build
import openpyxl
from io import BytesIO


def get_filenames():
    scopes = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = '/home/cusdeb/Projects/lizard_bot/lizardbot/lizardbot-423509-18b41a862983.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)

    drive_service = build('drive', 'v3', credentials=credentials)

    # Получаем список файлов расписания
    folder_id = '19yyXXullGGMIT3XISiZ33wkDxHJy0zvb'
    results = drive_service.files().list(q=f"'{folder_id}' in parents",
                                         fields="nextPageToken, files(id, name)").execute()
    files = results.get('files', [])

    return files


def download_file(file_id, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    file_content = BytesIO(request.execute())
    return file_content


def process_excel(file_content, group_name):
    wb = openpyxl.load_workbook(file_content)
    results = []

    for sheet in wb.worksheets:
        for row in sheet.iter_rows(min_row=2, values_only=True):
            for i in range(1, len(row), 3):
                if row[i] == group_name:
                    room_number = row[i - 1]
                    teacher_name = row[i + 1]
                    results.append((sheet.title, room_number, teacher_name))

    return results


def form_schedule(schedule):
    time_mapping = {1: '8:00-9:30', 2: '9:40-11:10', 3: '11:30-13:00', 4: '13:10-14:40', 5: '15:00-16:30',
                    6: '16:40-18:10', 7: '18:20-19:50'}

    schedule_text = schedule.split('\n')
    for i, line in enumerate(schedule_text):
        if line.strip() and line[0].isdigit():
            pair_number = int(line[0])
            print(pair_number)
            if pair_number in time_mapping:
                schedule_text[i] += f" {time_mapping[pair_number]}"

    updated_schedule = '\n'.join(schedule_text)
    return updated_schedule


def service(name, group):
    files = get_filenames()

    # Выводим список доступных файлов
    for index, file in enumerate(files):
        print(f"{index + 1}. {file['name']}")

    # Запрашиваем у пользователя ввод полного названия файла (без .xlsx)
    chosen_file_name = name

    chosen_file = None
    for file in files:
        if file['name'] == chosen_file_name + '.xlsx':
            chosen_file = file
            break

    if chosen_file is None:
        print("Файл не найден.")
        return

    group_name = group

    # Загружаем и обрабатываем выбранный файл
    scopes = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = '/home/cusdeb/Projects/lizard_bot/lizardbot/lizardbot-423509-18b41a862983.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    drive_service = build('drive', 'v3', credentials=credentials)

    file_content = download_file(chosen_file['id'], drive_service)
    results = process_excel(file_content, group_name)
    message = []
    # Выводим результаты
    print(f'{chosen_file["name"]}'.replace('.xlsx',''))
    for sheet_title, room_number, teacher_name in results:
        message.append(f"\n{sheet_title}, Кабинет: {room_number}, Преподаватель: {teacher_name}")

    return message


if __name__ == "__main__":
    service()
