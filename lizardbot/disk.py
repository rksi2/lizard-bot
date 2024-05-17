from google.oauth2 import service_account
from googleapiclient.discovery import build
import openpyxl
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

    # Выводим список доступных файлов
    for index, file in enumerate(files):
        print(f"{index + 1}. {file['name']}")

    # Запрашиваем у пользователя ввод полного названия файла (без .xlsx)
    chosen_file_name = input("Выберите дату: ")

    chosen_file = None
    for file in files:
        if file['name'] == chosen_file_name + '.xlsx':
            chosen_file = file
            break

    if chosen_file is None:
        print("Файл не найден.")
        return

    group_name = input("Введите название группы: ")

    # Загружаем и обрабатываем выбранный файл
    scopes = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = '/home/dredd/projects/lizard_bot/lizardbot-423609-db4df596a5a4.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    drive_service = build('drive', 'v3', credentials=credentials)

    file_content = download_file(chosen_file['id'], drive_service)
    results = process_excel(file_content, group_name)

    # Выводим результаты
    print(f'{chosen_file["name"]}'.replace('.xlsx',''))
    for sheet_title, room_number, teacher_name in results:
        print(f"{sheet_title}, {group_name}, Кабинет: {room_number}, Преподаватель: {teacher_name}")


if __name__ == "__main__":
    main()
