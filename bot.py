import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
import config

API_URL = "http://127.0.0.1:8000"

bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


# срабатывает, когда пользователь отправляет команду /start
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Начнем с минуса или плюса?\n"
    )


# срабатывает на любое текстовое сообщение
@dp.message()
async def handle_message(message: Message):
    # отправляем текст пользователя на наш сервер
    try:
        response = requests.post(
            API_URL + "/transactions/from-text",
            json={"text": message.text},
            timeout=30
        )
        data = response.json()
    except Exception:
        # сюда попадём, если сервер не запущен или недоступен
        await message.answer("Не могу связаться с сервером. Он точно запущен?")
        return

    # если сервер вернул успешный ответ - показываем результат
    if "message" in data:
        answer = (
            "Записал!\n"
            f"Сумма: {data['amount']} руб.\n"
            f"Тип: {data['type']}\n"
            f"Категория: {data['category']}"
        )
    else:
        answer = "Ответ сервера: " + str(data)
    await message.answer(answer)


# запускаем бота (он начинает слушать сообщения)
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())