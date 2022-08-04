from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from createbot import bot, dp
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from keyboards import admin_kb
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from database import sqlite_db
from googletable.gtable import GoogleSheet
import masters


class FSMadmin(StatesGroup):
	photo = State()
	name = State()
	description = State()

class FSMmailing(StatesGroup):
	mailing_text = State()

async def log_mod(message: types.Message):
	if message.from_user.id == masters.ADMIN_ID:
		await bot.send_message(message.from_user.id, "Вы вошли как Админ!!\
			\nДля Вас доступна <b>Загрузка</b> и 'Удаление'фото и 'Описаний'\
			\nесли вы на каком то этапе передумали это делать нажмите 'Отмена'\
			\nДля 'Загрузки' фото логотипа необходимо указать название фото 'logo'\
			\nДля 'Загрузки' фото Основного зала необходимо указать в начале названия фото 'oz'\
			\nДля 'Загрузки' фото Babby room необходимо указать в начале названия фото 'bb'\
			\nДля 'Загрузки' фото Оба зала необходимо указать в начале названия фото 'ro'\
			\nДля 'Загрузки' правил необходимо указать название фото 'ru' и в описание добавить правила\
			\n'Описание' необходимо указать к первому фото, к остальным фото можно написать любой символ", reply_markup=admin_kb.btnadmin)


# Начало диалога для загрузки 
async def cm_start(message : types.Message):
	if message.from_user.id == masters.ADMIN_ID:
		await FSMadmin.photo.set()
		await message.reply('Загрузи фото')

# выход на любой стадии админки
async def cancel_FSM(message: types.Message, state: FSMContext):
	if message.from_user.id == masters.ADMIN_ID:
		curent_state = await state.get_state()
		if curent_state is None:
			return
		await state.finish()
		await message.reply('Готово', reply_markup=ReplyKeyboardRemove())


# диалог для загрузки фото
async def load_photo(message: types.Message, state: FSMContext):
	if message.from_user.id == masters.ADMIN_ID:
		async with state.proxy() as data:
			data['photo'] = message.photo[0].file_id
		await FSMadmin.next()
		await message.reply('Введите название фото')

# диалог для загрузки названия фото
async def load_name(message: types.Message, state: FSMContext):
	if message.from_user.id == masters.ADMIN_ID:
		async with state.proxy() as data:
			data['name'] = message.text
		await FSMadmin.next()
		await message.reply('Введите описание')

# диалог для загрузки описания фото
async def load_description(message: types.Message, state: FSMContext):
	if message.from_user.id == masters.ADMIN_ID:
		async with state.proxy() as data:
			data['description'] = message.text
		await sqlite_db.sql_add_command(state)
		await state.finish()

#удаление файлов из бд
async def del_callback_run(call: types.CallbackQuery):
	await sqlite_db.sql_delete_command(call.data.replace('del ', ''))
	await call.answer(text=f'{call.data.replace("del ", "")} удалена', show_alert=True)

async def delete_item(message: types.Message):
	if message.from_user.id == masters.ADMIN_ID:
		read = await sqlite_db.sql_read()
		for ret in read:
			await bot.send_photo(message.from_user.id, ret[0], f'Название: {ret[1]}\nОписание: {ret[2]}')
			await bot.send_message(message.from_user.id, text='^', reply_markup=InlineKeyboardMarkup().\
				add(InlineKeyboardButton(f'Удалить {ret[1]}', callback_data=f'del {ret[1]}')))

async def send_all(message: types.Message):
	if message.from_user.id == masters.ADMIN_ID:
		await FSMmailing.mailing_text.set()
		await message.reply('Введите текст рассылки')

async def rec_description(message: types.Message, state: FSMContext):
	if message.from_user.id == masters.ADMIN_ID:
		global data
		async with state.proxy() as data:
			data['mailing_text'] = message.text
		await state.reset_state(with_data=False)
		await bot.send_message(chat_id=masters.ADMIN_ID, text='Отправляем?',
								reply_markup=InlineKeyboardMarkup(row_width=2).\
								insert(InlineKeyboardButton(text='Отправить', callback_data='Push')))
		await state.finish()

async def push_mailing(call: types.CallbackQuery):
	if call.data == 'Push':
		gs = GoogleSheet()
		range_sheet = 'Clients!A2:G'
		read = gs.read_sheet(range_sheet)
		count = 0
		for id_chat in range(0, len(read), 1):
			try:
				await bot.send_message(chat_id=read[id_chat][6], text=(f"{data['mailing_text']}"))
				
			except Exception as ex:
				count += 1
				await bot.send_message(chat_id=masters.ADMIN_ID, text=f'Сообщение не доставленно {count} пользователям')


def register_handlers_admin(dp : Dispatcher):
	dp.register_message_handler(cm_start, text=['Загрузить'], state=None)
	dp.register_message_handler(cancel_FSM, state="*", commands='отмена')
	dp.register_message_handler(cancel_FSM, Text(equals='отмена', ignore_case=True), state="*")
	dp.register_message_handler(load_photo, content_types=['photo'], state=FSMadmin.photo)
	dp.register_message_handler(load_name, state=FSMadmin.name)
	dp.register_message_handler(load_description, state=FSMadmin.description)
	dp.register_message_handler(log_mod, commands=['admin'], user_id=masters.ADMIN_ID)
	dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del '))
	dp.register_message_handler(delete_item, text=['Удалить'])
	dp.register_message_handler(send_all, text=['Рассылка'], state=None)
	dp.register_message_handler(rec_description, state=FSMmailing.mailing_text)
	dp.register_callback_query_handler(push_mailing, text_contains='Push')