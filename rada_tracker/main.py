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

laws_file = Path('../laws.json')
laws = json.load(laws_file.open('r'))


def check_law(law):
    print(f'Checking law: {law["name"]}')
    data = requests.get(law['url'])
    soup = BeautifulSoup(data.text, 'html5lib')

    pattern = re.compile(r'\d\d.\d\d.\d\d\d\d')
    dates = [dt.from_format(d, 'DD.MM.YYYY').date() for d in pattern.findall(soup.text)]
    print(f"Last update: {max(dates).format('DD.MM.YYYY')}")
    new_dates = [d for d in dates if d > dt.parse(law['updated']).date()]
    formatted_dates = [d.format('DD.MM.YYYY') for d in new_dates]
    for d in formatted_dates:
        bot.send_message(ALERT_CHANNEL, f'Найдено обновление закона!\n\n<a href="{law["url"]}">{law["name"]}'
                                        f'</a> обновлен {d}', parse_mode='HTML')


if __name__ == '__main__':
    print("Starting rada tracker")
    for l in laws:
        check_law(l)
    print("Sleeping 12 hours")
    time.sleep(12 * 60 * 60)


