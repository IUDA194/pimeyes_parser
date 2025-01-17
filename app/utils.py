import json
import os
from os import getenv

from dotenv import load_dotenv, find_dotenv

from aiogram.types import URLInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, html, F, Bot

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InputMediaPhoto

from app.find_same_photo import get_unique_images

load_dotenv(find_dotenv())

async def send_result(find_result, chat_id):
    try:
        bot = Bot(token=getenv("BOT_TOKEN"))
        if not find_result:
            await bot.send_message(chat_id, "Результаты не найдены. ⛔")
            return

        find_result = json.loads(find_result)
        results = find_result.get("results", [])

        # Извлекаем все thumbnail_url и проверяем на уникальность
        urls = [result.get("thumbnailUrl") for result in results if result.get("thumbnailUrl")]
        unique_urls = get_unique_images(urls)

        for result in results:
            thumbnail_url = result.get("thumbnailUrl")
            source_url = result.get("sourceUrl")
            image_url = result.get("imageUrl")

            # Пропускаем неуникальные или неполные записи
            if thumbnail_url not in unique_urls or not source_url or not image_url:
                continue

            # Создаем кнопки
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Полная картинка", url=image_url)
                ],
                [
                    InlineKeyboardButton(text="Источник", url=source_url),
                ]
            ])

            # Отправляем сообщение с картинкой и кнопками
            try:
                await bot.send_photo(chat_id=chat_id, photo=thumbnail_url, reply_markup=buttons)
            except Exception as e:
                print(f"Не удалось отправить фото с ссылкой {thumbnail_url}: {e}")
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"Произошла ошибка: {str(e)}")
