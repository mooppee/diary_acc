import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
import config

API_URL = "http://127.0.0.1:8000"

bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Я твой дневник-бухгалтер.\n"
        "Напиши операцию текстом, например:\n"
        "щебень на дс13 127600\n"
        "масло камаз 5000\n"
        "шуре зп 15000\n"
        "папа перевел 105000"
    )


@dp.message()
async def handle_message(message: Message):
    try:
        response = requests.post(API_URL + "/transactions/from-text",
                                 json={"text": message.text}, timeout=30)
        data = response.json()
    except Exception:
        await message.answer("Не могу связаться с сервером. Он точно запущен?")
        return

    if "message" in data:
        answer = "Записал!\n"
        answer += f"Сумма: {data['amount']} руб.\n"
        answer += f"Тип: {data['type']}\n"
        answer += f"Объект: {data['object']}\n"
        answer += f"Категория: {data['category']}\n"
        if data.get("subcategory"):
            answer += f"Подкатегория: {data['subcategory']}\n"
        if data.get("created"):
            answer += "\nНовое: " + ", ".join(data["created"])
    else:
        answer = "Не получилось записать операцию :("

    await message.answer(answer)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())