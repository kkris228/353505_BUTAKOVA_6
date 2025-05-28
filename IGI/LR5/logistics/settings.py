import os

# NewsAPI settings
NEWS_API_KEY = '32d1b27710904cbba6bf6015ca2ac85d'

# Безопасная конфигурация - если ключ задан в переменных окружения, используем его
if os.environ.get('NEWS_API_KEY'):
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY') 