import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

TOKEN = "7818257770:AAHkSbxTYPOFKzGWieQHkhIUa8lIRMcuuxY"  # Замените на ваш токен

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Кэш для хранения курсов
rates_cache = {}
last_update = None

async def fetch_nbrb_rates():
    global last_update, rates_cache
    
    # Если данные актуальны (обновлялись менее часа назад), возвращаем кэш
    if last_update and (datetime.now() - last_update) < timedelta(hours=1):
        return rates_cache
    
    try:
        # Получаем все курсы одним запросом
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Отбираем только USD, EUR и RUB
        target_currencies = {'USD', 'EUR', 'RUB'}
        new_rates = {}
        
        for item in data:
            if item['Cur_Abbreviation'] in target_currencies:
                code = item['Cur_Abbreviation']
                new_rates[code] = {
                    'rate': item['Cur_OfficialRate'],
                    'scale': item['Cur_Scale'],
                    'name': item['Cur_Name']
                }
        
        if new_rates:  # Если получили хотя бы один курс
            rates_cache = new_rates
            last_update = datetime.now()
            return rates_cache
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к API: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    return None

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    buttons = [
        types.InlineKeyboardButton(text="USD", callback_data="USD"),
        types.InlineKeyboardButton(text="EUR", callback_data="EUR"),
        types.InlineKeyboardButton(text="RUB", callback_data="RUB"),
        types.InlineKeyboardButton(text="Все курсы", callback_data="ALL")
    ]
    builder.add(*buttons)
    builder.adjust(3, 1)  # 3 кнопки в первом ряду, 1 во втором
    
    await message.answer(
        "🏦 <b>Курсы валют НБРБ</b>\n"
        "Выберите валюту:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@dp.callback_query()
async def handle_currency(callback: types.CallbackQuery):
    try:
        rates = await fetch_nbrb_rates()
        
        if not rates:
            await callback.message.edit_text("⚠️ Сервис курсов временно недоступен. Попробуйте позже.")
            await callback.answer()
            return
        
        currency = callback.data
        
        if currency == "ALL":
            text = "<b>Официальные курсы НБРБ:</b>\n"
            for code, data in sorted(rates.items()):
                text += (f"\n{data['name']} ({code}): "
                        f"<b>{data['rate']:.4f} BYN</b> "
                        f"(за {data['scale']} {code})")
            await callback.message.edit_text(text, parse_mode="HTML")
        elif currency in rates:
            data = rates[currency]
            text = (f"<b>{data['name']} ({currency})</b>\n"
                   f"Курс: <b>{data['rate']:.4f} BYN</b>\n"
                   f"За: {data['scale']} {currency}\n"
                   f"Обновлено: {last_update.strftime('%d.%m.%Y %H:%M')}")
            await callback.message.edit_text(text, parse_mode="HTML")
        else:
            await callback.message.edit_text("⚠️ Данная валюта временно недоступна")
        
        await callback.answer()
    
    except Exception as e:
        print(f"Ошибка в обработчике: {e}")
        await callback.answer("⚠️ Произошла ошибка. Попробуйте еще раз.")

@dp.message(Command("rates"))
async def cmd_rates(message: types.Message):
    try:
        rates = await fetch_nbrb_rates()
        
        if not rates:
            await message.answer("⚠️ Сервис курсов временно недоступен. Попробуйте позже.")
            return
        
        text = "<b>Официальные курсы НБРБ:</b>\n"
        for code, data in sorted(rates.items()):
            text += (f"\n{data['name']} ({code}): "
                    f"<b>{data['rate']:.4f} BYN</b> "
                    f"(за {data['scale']} {code})")
        
        await message.answer(text, parse_mode="HTML")
    
    except Exception as e:
        print(f"Ошибка в команде rates: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте еще раз.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())