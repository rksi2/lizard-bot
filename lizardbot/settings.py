"""Модуль настроек проекта."""

import os

from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL', 'http://127.0.0.1:8000')

SAVE_LATEST_MESSAGE = True

TIMEOUT = 10

TOKEN = os.getenv('TOKEN', '')
