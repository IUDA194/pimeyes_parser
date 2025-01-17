import time
from os import getenv
import asyncio

from dotenv import load_dotenv, find_dotenv

from aiogram import Router, html, F, Bot

from app.parser import find_face
from app.utils import send_result
from app.redis_client import RedisClient
from app.text_from_photo import get_ansver

load_dotenv(find_dotenv())


redis_c = RedisClient()
redis_c.connect()

async def main():
    while True:
        search = redis_c.pop_from_queue(queue_name="search-face")
        if search:
            id, path, chat_id = search.split(":")
            
            await Bot(token=getenv("BOT_TOKEN")).send_message(chat_id=chat_id, text=f"Обрабатываем фотографию с {id}")
            try:
                description = get_ansver(path=path)
                await Bot(token=getenv("BOT_TOKEN")).send_message(chat_id=chat_id, text=f"{description}")
            except:
                await Bot(token=getenv("BOT_TOKEN")).send_message(chat_id=chat_id, text=f"Случилась ошибка при обработке фотографии!")
            
            await Bot(token=getenv("BOT_TOKEN")).send_message(chat_id=chat_id, text=f"Обработка фотографий по {id} 🔎")
            
            results = find_face(path=path)

            await send_result(results, chat_id)
        else: 
            print("Очередь пуста")
            time.sleep(3)

asyncio.run(main())