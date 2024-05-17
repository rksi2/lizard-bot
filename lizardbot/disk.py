from google.oauth2 import service_account
from googleapiclient.discovery import build
import openpyxl
import requests
from io import BytesIO


def get_filenames():
    scopes = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = '/home/dredd/projects/lizard_bot/lizardbot-423609-db4df596a5a4.json'
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


def main():
    files = get_filenames()
    group_name = "ИС-12"

    # Выводим список доступных файлов
    print("Доступные файлы:")
    for index, file in enumerate(files):
        print(f"{index + 1}. {file['name']}")

    # Запрашиваем у пользователя выбор файла
    file_index = int(input("Выберите дату: ")) - 1

    if file_index < 0 or file_index >= len(files):
        print("Неверный выбор файла.")
        return

    chosen_file = files[file_index]

    # Загружаем и обрабатываем выбранный файл
    scopes = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = '/home/dredd/projects/lizard_bot/lizardbot-423609-db4df596a5a4.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    drive_service = build('drive', 'v3', credentials=credentials)

    file_content = download_file(chosen_file['id'], drive_service)
    results = process_excel(file_content, group_name)

    # Выводим результаты
    print(f"{chosen_file['name']}")
    for sheet_title, room_number, teacher_name in results:
        print(f"{sheet_title}, {group_name}, Кабинет: {room_number}, Преподаватель: {teacher_name}")


if __name__ == "__main__":
    main()
