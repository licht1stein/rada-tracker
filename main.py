import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import re
import pendulum as dt
import json

from telegram import Bot

from envparse import env

env.read_envfile()

BOT_TOKEN = env("BOT_TOKEN")
ALERT_CHANNEL = env('ALERT_CHANNEL')

bot = Bot(BOT_TOKEN)

laws_file = Path('laws.json')
laws = json.load(laws_file.open('r'))


def check_law(law):
    print(f'Проверка обновлений: {law["name"]}')
    data = requests.get(law['url'])
    soup = BeautifulSoup(data.text, 'html5lib')

    pattern = re.compile(r'\d\d.\d\d.\d\d\d\d')
    dates = [dt.from_format(d, 'DD.MM.YYYY').date() for d in pattern.findall(soup.text)]

    expected_updated = dt.parse(law['updated']).date()
    actual_updated = max(dates)
    print(f'Ожидаемое последнее обновление: {expected_updated.format("DD.MM.YYYY")}')
    print(f"Фактическое последнее обновление: {actual_updated.format('DD.MM.YYYY')}")

    if expected_updated < actual_updated:
        bot.send_message(ALERT_CHANNEL, f'Найдено обновление закона!\n\n<a href="{law["url"]}">{law["name"]}'
                                        f'</a> обновлен {actual_updated.format("DD.MM.YYYY")}', parse_mode='HTML')
    else:
        print(f"Без изменений: {law['name']}")


if __name__ == '__main__':
    print("rada-tracker: запуск")
    for l in laws:
        check_law(l)
    print("Ждем 12 часов")
    time.sleep(12 * 60 * 60)


