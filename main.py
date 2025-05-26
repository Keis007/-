import asyncio


from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

TOKEN = "7818257770:AAHkSbxTYPOFKzGWieQHkhIUa8lIRMcuuxY"

dp = Dispatcher()

# Command handler
@dp.message(Command("start"))
async def cmd_random(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Курс",
        callback_data="get course")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы получить курс",
        reply_markup=builder.as_markup()
    )
    
@dp.message(Command("course"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Курс РБ")

@dp.callback_query(F.data == "get course")
async def send_random_value(callback: CallbackQuery):
    await callback.message.answer("гулинский")

# Run the bot
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
          
         