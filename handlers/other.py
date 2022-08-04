from aiogram import types, Dispatcher
from createbot import bot



async def price(message: types.Message):
	await message.reply('С удовольствием Вам помогу!!\nЦена:\nОсновной зал: 1600 руб.\час\nBaby room : 900 руб.\час\nОба зала: 2000 руб.\час')

async def price1(message: types.Message):
	await message.reply('С удовольствием Вам помогу!!\nЦена:\nОсновной зал: 1600 руб.\час\nBaby room : 900 руб.\час\nОба зала: 2000 руб.\час')

async def price2(message: types.Message):
	await message.reply('С удовольствием Вам помогу!!\nЦена:\nОсновной зал: 1600 руб.\час\nBaby room : 900 руб.\час\nОба зала: 2000 руб.\час')

async def echo_send(message: types.Message):
	await message.reply('Я не знаю такую команду, вот команда которую я знаю: /start')
		



def register_handlers_other(dp : Dispatcher):
	dp.register_message_handler(price, lambda message: 'цена' in message.text)
	dp.register_message_handler(price1, lambda message: 'стоит' in message.text)
	dp.register_message_handler(price2, lambda message: 'стоимость' in message.text)
	dp.register_message_handler(echo_send)
	