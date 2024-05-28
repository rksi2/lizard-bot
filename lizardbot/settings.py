"""Модуль настроек проекта."""

import os

from dotenv import load_dotenv

load_dotenv()

API_HOST = os.getenv('API_HOST')
API_PORT = os.getenv('API_PORT')

TOKEN = os.getenv('TOKEN', '')

SAVE_LATEST_MESSAGE = True
