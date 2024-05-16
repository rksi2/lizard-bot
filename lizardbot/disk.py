from google.oauth2 import service_account
from googleapiclient.discovery import build


def get_filenames():
    scopes = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = '/home/cusdeb/Projects/lizard_bot/lizardbot/lizardbot-423509-18b41a862983.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)

    drive_service = build('drive', 'v3', credentials=credentials)

    # Получаем список файлов расписания
    folder_id = '19yyXXullGGMIT3XISiZ33wkDxHJy0zvb'
    results = drive_service.files().list(q=f"'{folder_id}' in parents", fields = "nextPageToken, files(id,name)").execute()
    files = results.get('files', [])
    return files

