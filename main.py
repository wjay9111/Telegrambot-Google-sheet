from datetime import datetime, timedelta
from aiogram.utils import executor
from createbot import dp, bot
from database import sqlite_db
from handlers import *
from aiogram.utils.emoji import emojize
from googletable.gtable import GoogleSheet
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import aioschedule
import logging

logging.basicConfig(filename='logging.log',
					level=logging.INFO,
					format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
					)
log = logging.getLogger("ex")

try:
	raise RuntimeError
except Exception:
	log.info('INFO')
	log.error('ERROR!!')
	log.debug('DEBUG')

gs = GoogleSheet()
range_sheet = 'Clients!A2:G'
	
async def on_startup(_):
	print('Бот вышел в онлайн')
	await bot.send_message(chat_id=admin.ADMIN_ID, text=emojize('Я онлайн, и готов работать :wink: /start'))
	sqlite_db.sql_start()
	asyncio.create_task(loop_schedule())

async def reminder_client():
	try:
		read = gs.read_sheet(range_sheet)
		date_now = (datetime.now() + timedelta(1)).strftime('%d.%m.%Y')
		for id_chat in range(0, len(read), 1):
			if date_now == read[id_chat][2]:
				await bot.send_message(chat_id=read[id_chat][6], text=emojize(f'Добрый день напоминаю\nЗавтра вы :pencil2: записаны в фотостудию Hygge \nВремя:  {read[id_chat][3]}'))
	except Exception as ex:
		print(ex)

async def feed_back():
	try:
		read = gs.read_sheet(range_sheet)
		date_now = (datetime.now() + timedelta(-1)).strftime('%d.%m.%Y')
		for id_chat in range(0, len(read), 1):
			if date_now == read[id_chat][2]:
				await bot.send_message(chat_id=read[id_chat][6], 
										text=emojize(f'Спасибо, что выбрали нас!\
													\nПожалуйста, оцените нашу работу\
													\nЗа ответ скидка 5% на следующее посещение💚)'), 
										reply_markup=InlineKeyboardMarkup(row_width=1).\
										insert(InlineKeyboardButton(text=emojize(':blush: Щас как напишу Вам отзыв! :kissing_heart:'), callback_data='feed_back_yes')).\
										insert(InlineKeyboardButton(text=emojize(':rage: Нехочу писать, вы вонючки :shit:'), callback_data='feed_back_no'))
										)
										
	except Exception as ex:
		print(ex)

async def loop_schedule():
	try:
		aioschedule.every().day.at("14:00").do(reminder_client)
		aioschedule.every().day.at("12:10").do(feed_back)
		while True:
			await aioschedule.run_pending()
			await asyncio.sleep(1)
	except Exception as ex:
		print(ex)

admin.register_handlers_admin(dp)
client.register_handlers_client(dp)
# admin.register_handlers_admin(dp)
other.register_handlers_other(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)