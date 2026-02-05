"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '8399906862:AAGztEPgwD6QgI2AOnKo0yF8_I8jYiOfpyY')

# URL для webhook (для Render)
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')

# Интервал проверки новых прогнозов (в секундах)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 минут

# База данных
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///predictions_bot.db')

# URL Sports.ru
SPORTS_RU_URL = 'https://www.sports.ru'
PREDICTIONS_URL = f'{SPORTS_RU_URL}/predictions/'

# Партнерская ссылка по умолчанию
DEFAULT_PARTNER_URL = 'https://spnsrd.ru/hub/prognoz/baltbet'

# Виды спорта (будут использоваться для фильтрации)
SPORTS = {
    'football': '⚽️ Футбол',
    'hockey': '🏒 Хоккей',
    'basketball': '🏀 Баскетбол',
    'tennis': '🎾 Теннис',
}

# Популярные турниры для каждого вида спорта
TOURNAMENTS = {
    'football': [
        'РПЛ',
        'АПЛ',
        'Ла Лига',
        'Серия А',
        'Бундеслига',
        'Лига 1',
        'Лига чемпионов',
        'Лига Европы',
        'Кубок России',
    ],
    'hockey': [
        'КХЛ',
        'НХЛ',
        'МХЛ',
    ],
    'basketball': [
        'НБА',
        'Евролига',
        'Единая лига ВТБ',
    ],
    'tennis': [
        'Australian Open',
        'Roland Garros',
        'Wimbledon',
        'US Open',
    ],
}

# Максимальное количество символов в кратком описании прогноза
MAX_DESCRIPTION_LENGTH = 500

# Порт для webhook (для Render)
PORT = int(os.getenv('PORT', '8443'))
