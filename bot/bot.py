import json
import logging
import random
import re

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_webhook
from bot.config import (BOT_TOKEN, HEROKU_APP_NAME,
                          WEBHOOK_URL, WEBHOOK_PATH,
                          WEBAPP_HOST, WEBAPP_PORT)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
Quran = json


class NotDigit(Exception):
    pass


class IncorrectSurah(Exception):
    pass


class IncorrectAyah(Exception):
    pass


def correct(msg):
    explanation_index = msg.find('***')
    if (explanation_index > -1):
        msg = msg[:explanation_index]
    ending_index = msg.find('Милостью Всевышнего тафсир')
    if (ending_index > -1):
        msg = msg[:ending_index]
    if len(msg) > 4096:
        msg = msg[:4097]
        for i in range(4095, 0, -1):
            if msg[i] == '.':
                msg = msg[:i + 1]
                break
    return msg


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(
        "Ас-саляму алейкум! Напиши /random, чтобы прочитать случайный аят, или отправь номер суры и аята!")


@dp.message_handler(commands="random")
async def get_random_verse(message: types.Message):
    num = random.randint(1, 114)
    vnum = random.randint(0, len(Quran[str(num)]) - 1)
    verses = Quran[str(num)].items()
    rnum = ""
    rtext = ""
    for n, t in verses:
        if vnum == 0:
            rnum = n
            rtext = t
            break
        vnum -= 1
    await message.answer(correct(rnum + rtext))


@dp.message_handler()
async def reply(message: types.Message):
    surah, ayah = re.split(', | |:|,', message.text)
    msg = ""
    try:
        if not surah.isdigit() or not ayah.isdigit():
            raise NotDigit
        print("nums got", surah, ayah)
        if 0 < int(surah) < 115:
            verses = Quran[surah].items()
            for n, t in verses:
                print("trying")
                nums = list(map(int, re.split('[-:,]', n)))
                if nums[1] <= int(ayah) <= nums[-1]:
                    print("I find!")
                    msg = n + t
                    break
            if len(msg) == 0:
                raise IncorrectAyah
        else:
            raise IncorrectSurah
    except NotDigit:
        msg = "Not number"
    except IncorrectSurah:
        msg = "Surah isn't correct"
    except IncorrectAyah:
        msg = "Ayah isn't correct"
    except Exception as ex:
        print("Something goes wrong!!!")
        print(ex)
    await message.answer(correct(msg))


async def on_startup(dp):
    logging.warning(
        'Starting connection. ')
    await bot.set_webhook(WEBHOOK_URL,drop_pending_updates=True)


async def on_shutdown(dp):
    logging.warning('Bye! Shutting down webhook connection')


def main():
    with open("Quran.json", encoding='utf-8') as file:
        Quran = json.load(file)

    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )