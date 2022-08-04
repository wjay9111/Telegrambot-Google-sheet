from aiogram import types
from createbot import dp, bot
from aiogram.types.message import ContentType
from database import sqlite_db
from googletable.gtable import GoogleSheet
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.emoji import emojize
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
import masters



class FSMclient(StatesGroup):
	fsm = State()
	name = State()
	phone = State()		

class FSMfedback(StatesGroup):
	feedback_text = State()
	
gs = GoogleSheet()
range_sheet_f_room = 'Calendar!A1:M'
range_sheet_b_room = 'Calendar BB!A1:M'
sheet_client = 'Clients!A2'
feedback_sheet_id = 'Clients!G2:G'

# функция создания клавиатуры даты и времени
def get_kb(free_date):
		keyboard = InlineKeyboardMarkup(row_width=3)
		for date in free_date:
			btn = InlineKeyboardButton(text=date, callback_data=date)
			keyboard.insert(btn)
		
		return keyboard

# функция выбора даты для записи клиентов

def select_date_first_room():
	free_date = gs.free_date(range_sheet_f_room)	
	return free_date

def select_date_baby_room():
	free_date = gs.free_date(range_sheet_b_room)	
	return free_date

def select_date_two_rooms():
	free_date = []
	free_date_first = []
	free_date_baby = []
	free_date_f_room = gs.free_date(range_sheet_f_room)
	free_date_b_room = gs.free_date(range_sheet_b_room)
	for free_date_f in free_date_f_room:	
		free_date_first.append(free_date_f)
	for free_date_b in free_date_b_room:
		free_date_baby.append(free_date_b)
	
	if free_date_first == free_date_baby:
		for freedate in free_date_first:
			free_date.append(freedate)

	
	else:
		result = [i for i, j in zip(free_date_first, free_date_baby) if i == j]
		for freedate in result:	
			free_date.append(freedate)

	return free_date

def getDateChoose(room):
	if 'room' in room:
		if room['room'] == 'First_room':
			date_choose = select_date_first_room()
			return date_choose
		if room['room'] == 'Baby_room':
			date_choose = select_date_baby_room()
			return date_choose
		if room['room'] == 'Two_rooms':
			date_choose = select_date_two_rooms()
			return date_choose

# Стартовый диалог
async def command_start(message: types.Message, state: FSMContext):                                
	try:

		logo = sqlite_db.sql_read_logo()
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		btn_start = types.InlineKeyboardButton(text="Начать!", callback_data="start")
		keyboard.add(btn_start)
		
		await bot.send_photo(message.from_user.id, logo[0], caption=logo[1], reply_markup=keyboard)
		print(message.from_user.id)
		async with state.proxy() as data:
			data['id_chat'] = int(message.from_user.id)

		st_db = None
		sqlite_db.sql_add_pre_records(st_db, data['id_chat'])
		
	except Exception as ex:
			print(ex)

async def start_view(call: types.CallbackQuery):
	sql = sqlite_db.sql_read_pre_records(int(call.from_user.id))
	if sql[5] != 'Null':
		await bot.send_message(call.from_user.id, text='Дождитесь подтверждения первой брони!!!')
	else:
		await call.answer()
		keyboardmain = types.InlineKeyboardMarkup(row_width=2)
		record_rooms = types.InlineKeyboardButton(text=emojize(":pencil2: Записаться :pencil2:"), callback_data="rooms")
		photo_rooms = types.InlineKeyboardButton(text=emojize(":camera: Фото локаций :camera:"), callback_data="photo_rooms")
		rules_rooms = types.InlineKeyboardButton(text=emojize(":scroll: Правила :scroll:"), callback_data="rules")
		keyboardmain.add(record_rooms, photo_rooms, rules_rooms)

		await bot.send_message(call.message.chat.id, text=emojize("Вот что я умею :sunglasses:"), reply_markup=keyboardmain)
		await bot.delete_message(call.from_user.id, call.message.message_id)
		await FSMclient.fsm.set()

async def select_place(call: types.CallbackQuery, state: FSMContext):  	
	
	async with state.proxy() as st:
		cur_state = st
	await state.reset_state(with_data=False)
	
	date_choose = getDateChoose(cur_state)
	time_list = ['09:00','10:00', '11:00', '12:00', 
				 '13:00', '14:00', '15:00', '16:00', 
				 '17:00', '18:00', '19:00', '20:00'
				]
	
	if call.data == "mainmenu":
		keyboardmain = types.InlineKeyboardMarkup(row_width=2)
		record_rooms = types.InlineKeyboardButton(text=emojize(":pencil2: Записаться :pencil2:"), callback_data="rooms")
		photo_rooms = types.InlineKeyboardButton(text=emojize(":camera: Фото локаций :camera:"), callback_data="photo_rooms")
		rules_rooms = types.InlineKeyboardButton(text=emojize(":scroll: Правила :scroll:"), callback_data="rules")
		keyboardmain.add(record_rooms, photo_rooms, rules_rooms)
	 	
		await bot.edit_message_text(chat_id=call.message.chat.id,
	 								message_id=call.message.message_id,
	 								text="Вот что я умею ",
	 								reply_markup=keyboardmain
	 	)
		await call.answer()

	if call.data == 'rules':
		keyboardmain = types.InlineKeyboardMarkup(row_width=2)
		backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
		keyboardmain.add(backbutton)
		rules = sqlite_db.sql_read_rules()
		await bot.edit_message_text(chat_id=call.message.chat.id,
									message_id=call.message.message_id,
									text=emojize(rules[0]["caption"]),
									reply_markup=keyboardmain
									)
		await call.answer()

	if call.data == 'photo_rooms':
		try:
			keyboardmain = types.InlineKeyboardMarkup(row_width=2)
			first_room = types.InlineKeyboardButton(text=emojize(":bomb: Основной зал :bomb:"), callback_data="First_room_photo")
			baby_room = types.InlineKeyboardButton(text=emojize(":baby: Baby_room :baby:"), callback_data="Baby_room_photo")
			backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
			keyboardmain.add(first_room, baby_room, backbutton)	
			await bot.edit_message_text(chat_id=call.message.chat.id,
										message_id=call.message.message_id,
										text=emojize(":camera: Фото локаций :camera:"),
										reply_markup=keyboardmain
										)
			await call.answer()
		
		except Exception as ex:
			print(ex)

	if call.data == 'First_room_photo':
		try:
			group = sqlite_db.sql_read_first_room()
			await bot.send_media_group(call.message.chat.id, group)
			await call.answer()
			
			keyboardmain = types.InlineKeyboardMarkup(row_width=1)
			first_room = types.InlineKeyboardButton(text=emojize(":pencil2: Записаться :pencil2:"), callback_data="First_room")
			backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
			keyboardmain.add(first_room, backbutton)
			await bot.send_message(call.from_user.id, emojize(":camera: Фото локаций :camera:"), reply_markup=keyboardmain)
		
		except Exception as ex:
			print(ex)
	
	if call.data == 'Baby_room_photo':
		try:	
			group = sqlite_db.sql_read_baby_room()
			await bot.send_media_group(call.message.chat.id, group)
			await call.answer()
			
			keyboardmain = types.InlineKeyboardMarkup(row_width=1)
			baby_room = types.InlineKeyboardButton(text=emojize(":pencil2: Записаться :pencil2:"), callback_data="Baby_room")
			backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
			keyboardmain.add(baby_room, backbutton)
			await bot.send_message(call.from_user.id, emojize(":camera: Фото локаций :camera:"), reply_markup=keyboardmain)
		
		except Exception as ex:
			print(ex)

	if call.data == 'rooms':
		try:
			keyboardmain = types.InlineKeyboardMarkup(row_width=1)
			first_room = types.InlineKeyboardButton(text=emojize(":bomb: Основной зал :bomb:"), callback_data="First_room")
			baby_room = types.InlineKeyboardButton(text=emojize(":baby: Baby_room :baby:"), callback_data="Baby_room")
			two_rooms = types.InlineKeyboardButton(text=emojize(":four_leaf_clover: Оба зала :four_leaf_clover:"), callback_data="Two_rooms")
			backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
			keyboardmain.add(first_room, baby_room, two_rooms, backbutton)
			await bot.edit_message_text(chat_id=call.message.chat.id,
										message_id=call.message.message_id,
										text="Выберете пространство для аренды",
										reply_markup=keyboardmain
										)

		except Exception as ex:
			print(ex)
	
	if call.data == 'Two_rooms':
		try:
			async with state.proxy() as data:
				data['room'] = call.data
			await state.reset_state(with_data=False)
			sqlite_db.sql_add_pre_records(data, data['id_chat'])

			group = sqlite_db.sql_read_rooms()
			keyboard = types.InlineKeyboardMarkup(row_width=2)
			call_photo = types.InlineKeyboardButton(text="Нужен фотограф", callback_data="photo")
			call_no_photo = types.InlineKeyboardButton(text="Только аренда зала", callback_data="nophoto")
			backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
			keyboard.add(call_photo, call_no_photo, backbutton)
			await bot.edit_message_text(chat_id=call.message.chat.id,
										message_id=call.message.message_id,
										text=group[0]["caption"],
										reply_markup=keyboard
			)
			await call.answer()
		
		except Exception as ex:
			print(ex)	
	
	if call.data == "First_room":
		try:
			async with state.proxy() as data:
				data['room'] = call.data
			await state.reset_state(with_data=False)
			sqlite_db.sql_add_pre_records(data, data['id_chat'])

			group = sqlite_db.sql_read_first_room()
			keyboard = types.InlineKeyboardMarkup(row_width=2)
			call_photo = types.InlineKeyboardButton(text="Нужен фотограф", callback_data="photo")
			call_no_photo = types.InlineKeyboardButton(text="Только аренда зала", callback_data="nophoto")
			backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
			keyboard.add(call_photo, call_no_photo, backbutton)
			await bot.edit_message_text(chat_id=call.message.chat.id, 
										message_id=call.message.message_id, 
										text=group[0]["caption"], 
										reply_markup=keyboard
										)
			await call.answer()
		
		except Exception as ex:
			print(ex)
	
	if call.data == "Baby_room":
		try:
			async with state.proxy() as data:
				data['room'] = call.data
			await state.reset_state(with_data=False)
			sqlite_db.sql_add_pre_records(data, data['id_chat'])

			group = sqlite_db.sql_read_baby_room()
			keyboard = types.InlineKeyboardMarkup(row_width=2)
			call_photo = types.InlineKeyboardButton(text="Нужен фотограф", callback_data="photo")
			call_no_photo = types.InlineKeyboardButton(text="Только аренда зала", callback_data="nophoto")
			backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
			keyboard.add(call_photo, call_no_photo,backbutton)
			await bot.edit_message_text(chat_id=call.message.chat.id, 
										message_id=call.message.message_id, 
										text=group[0]["caption"], 
										reply_markup=keyboard
										)
			await call.answer()
		
		except Exception as ex:
			print(ex)

	if call.data == "photo" :
		try:
			async with state.proxy() as data:
				data['photograph'] = call.data
			await state.reset_state(with_data=False)
			sqlite_db.sql_add_pre_records(data, data['id_chat'])
			
			keyboard_date = get_kb(date_choose)
			await bot.answer_callback_query(callback_query_id=call.id, 
											show_alert=True, 
											text="Стоимость фотографа оплачивается отдельно, он свяжется с вами после записи"
											)
			backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
			keyboard_date.add(backbutton)
			await bot.edit_message_text(chat_id=call.message.chat.id, 
										message_id=call.message.message_id, 
										text=emojize(":calendar: Выберете Дату :calendar:"), 
										reply_markup=keyboard_date
										)
			await call.answer()
		
		except Exception as ex:
			print(ex)

	if call.data == "nophoto" :
		try:
			async with state.proxy() as data:
				data['photograph'] = call.data
			await state.reset_state(with_data=False)
			sqlite_db.sql_add_pre_records(data, data['id_chat'])

			keyboard_date = get_kb(date_choose)
			backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
			keyboard_date.add(backbutton)
			await bot.edit_message_text(chat_id=call.message.chat.id, 
										message_id=call.message.message_id, 
										text=emojize(":calendar: Выберете Дату :calendar:"), 
										reply_markup=keyboard_date
										)
			await call.answer()
		
		except Exception as ex:
			print(ex)
	
	if 'room' in cur_state:
		if call.data in date_choose :
			try:
				async with state.proxy() as data:
					data['date'] = call.data
				await state.reset_state(with_data=False)
				sqlite_db.sql_add_pre_records(data, data['id_chat'])


				if data['room'] == 'First_room':
					free_time= gs.free_time(call.data, range_sheet_f_room)
					# exist_record = sqlite_db.sql_read_pre_records_date(data['date'])# не работает проверка, исправить
					# for req in free_time:
					# 	if req in exist_record:
					# 		free_time.remove(req)
					keyboard_time = get_kb(free_time)

				if data['room'] == 'Baby_room':
					free_time = gs.free_time(call.data,range_sheet_b_room)
					# exist_record = sqlite_db.sql_read_pre_records_date(data['date'])# не работает проверка, исправить
					# for req in exist_record:
					# 	if req in free_time:
					# 		free_time.remove(req)	
					keyboard_time = get_kb(free_time)

				if data['room'] == 'Two_rooms':
					def sort_freetime(free_time):
						return free_time[0:2]
					free_time = []
					free_time_first = []
					free_time_baby = []
					free_time_f_room = gs.free_time(call.data, range_sheet_f_room)
					free_time_b_room = gs.free_time(call.data,range_sheet_b_room)
					for free_time_f in free_time_f_room:	
						free_time_first.append(free_time_f)
					for free_time_b in free_time_b_room:
						free_time_baby.append(free_time_b)
					if free_time_first == free_time_baby:
						for freetime in free_time_first:
							free_time.append(freetime)	
							
					
					else:
						result = set(free_time_first).intersection(free_time_baby)
						for freetime in result:	
							free_time.append(freetime)
					free_time.sort(key=sort_freetime)		
					keyboard_time = get_kb(free_time)

				backbutton = types.InlineKeyboardButton(text=emojize(":back:"), callback_data="mainmenu")
				keyboard_time.add(backbutton)
				await bot.edit_message_text(chat_id=call.message.chat.id, 
											message_id=call.message.message_id, 
											text=emojize(":watch: Свободное время :watch:"),
											reply_markup=keyboard_time
											)
				await call.answer()
			
			except Exception as ex:
				print(ex)

	if call.data in time_list :
		try:
			async with state.proxy() as data:
				data['time'] = call.data
			await state.reset_state(with_data=False)
			sqlite_db.sql_add_pre_records(data, data['id_chat'])
			
			# if data['room'] == 'First_room':
			# 	gs = GoogleSheet()
			# 	range_sheet  = 'Calendar!A1:M'
			# 	free_time = gs.free_time(call.data, range_sheet)
			# 	exist_record = sqlite_db.sql_read_pre_records_date(data['time'])
			# 	for req in exist_record:
			# 		if req in free_time:
			# 			free_time.remove(req)

			# else:
			# 	gs = GoogleSheet()
			# 	range_sheet = 'Calendar BB!A1:M'
			# 	free_time = gs.free_time(call.data,range_sheet)
			# 	exist_record = sqlite_db.sql_read_pre_records_date(data['time'])
			# 	for req in exist_record:
			# 		if req in free_time:
			# 			free_time.remove(req)	

			await FSMclient.name.set()
			await bot.delete_message(call.from_user.id, call.message.message_id)
			await bot.send_message(call.from_user.id, 'Как Вас зовут ?')
			await call.answer()
		
		except Exception as ex:
			print(ex)

async def cl_name(message: types.Message, state: FSMContext):
	try:
		async with state.proxy() as data:
			data['name'] = message.text
		sqlite_db.sql_add_pre_records(data, data['id_chat'])

		await FSMclient.next()
		await message.reply(emojize(':phone: Напишите Ваш номер телефона :phone:'))
		
	except Exception as ex:
			print(ex)

async def cl_phone(message: types.Message, state: FSMContext):
	try:
		async with state.proxy() as data:
			data['phone'] = message.text.replace('-', '')
	
		sqlite_db.sql_add_pre_records(data, data['id_chat'])

		print(data)
		close = 'cancel_' + str(data['id_chat']) 
		confirmpay = 'cancell_' + str(data['id_chat']) 
		await state.finish()
		await bot.send_message(message.from_user.id, text=emojize(f"Для подтверждения брони, необходимо произвести\
		 оплату в течение 1 часа.\n\nРеквизиты для оплаты:\nСбербанк, {masters.name} 💳 {masters.card} 💳\n\nПосле\
		  поступления платежа, Вам придет потдверждение записи.\nтел.{masters.phone}"))
		await bot.send_message(chat_id=masters.ADMIN_ID, text=f"У нас новый клиент\nИмя: {data['name']}\
		 \nТел: {data['phone']}\nДата: {data['date']}\nВремя: {data['time']}\nЗал: {data['room']}")
		await bot.send_message(chat_id=masters.ADMIN_ID, text='Подтверждение оплаты',\
								reply_markup=InlineKeyboardMarkup(row_width=2).insert(\
								InlineKeyboardButton(text='Оплачено', callback_data=confirmpay)).insert(\
								InlineKeyboardButton(text='Отмена', callback_data=close)))
		# await bot.send_message(call.from_user.id, 'Забронировать', reply_markup=client_kb.inlainbutton4)
	except Exception as ex:
			print(ex)
	
# 3 функции платежного терминала
async def payments(call: types.CallbackQuery):             
	await bot.delete_message(call.from_user.id, call.message.message_id)
	await bot.send_invoice(chat_id=call.from_user.id, 
							title='Оплата', 
							description='Бронь на время 18:00', 
							payload='mypay', 
							provider_token=YOOTOKEN, 
							currency='RUB', 
							start_parameter='test_bot', 
							prices=[{"label": "Руб", "amount": 15000}]
							)
	print('работает1')

async def onpay(pre_checkout_query: types.PreCheckoutQuery):
	await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
	print('работает2')

async def process_pay(message: types.Message):
	if message.successful_payment.invoice_payload == 'mypay':
		await bot.send_message(message.from_user.id, 'Оплата успешно прошла. бла бла бла')
		print('работает3')

# Подтверждение оплаты администратором
async def confirm_pay(call: types.CallbackQuery):
	try:
		if 'cancel_' in call.data:
			cancel = call.data.split('_')
			cl = sqlite_db.sql_read_pre_records(cancel[1])
			
			await bot.send_message(chat_id=cl[6], text=emojize(':bangbang: :no_entry: Ваша оплата не подтверждена :confused: свяжитесь с нами по тел.8 (928) 419 36 41 :bangbang:'))
			await bot.delete_message(call.from_user.id, call.message.message_id)
			await call.answer()
			
			sqlite_db.sql_delete_pre_records(cl[6])
			print('Бронь отменена\nДанные успешно удалены из Database!! ')

		if 'cancell_' in call.data:
			pay = call.data.split('_')
			cl = sqlite_db.sql_read_pre_records(pay[1])

			if cl[1] == 'Two_rooms':
				room_text = 'Оба зала'
			if cl[1] == 'First_room':
				room_text = 'Основной зал'
			if cl[1] == 'Baby_room':
				room_text = 'Baby room'
			if cl[0] == 'photo':
				photographer = 'С фотографом'
			if cl[0] == 'nophoto':
				photographer = 'Без фотографа'
			
			time_h = int(cl[3][0:2]) * 100
			client_rec_sheet= [[cl[4], cl[-2], cl[2][3:], time_h, room_text, photographer, cl[6]]]
			
			await bot.send_message(chat_id=cl[6],
								   text=emojize(f"Оплата прошла успешно :+1:\
								    :fire: , вы записаны на:\nДата: {cl[2]}\nВремя:\
			{cl[3]}\nЗал: {room_text}\nАдрес: Краснодар, ул. Зиповская 5, литер Б, второй этаж,\
			 оф 207\n\nБудем вас ждать🌿 ")
								   )
			await bot.delete_message(call.from_user.id, call.message.message_id)
			await call.answer()
			sqlite_db.sql_delete_pre_records(cl[6])
			gs.appendRangeValues(sheet_client, client_rec_sheet)
			print('Бронь подтверждена\nДанные успешно удалены из Database!! ')
	except Exception as ex:
			print(ex)

async def feedback_start(call: types.CallbackQuery, state: FSMContext):
	if call.data == 'feed_back_yes':
		await bot.send_message(call.from_user.id, text=emojize('С удовольствием выслушаю ваши пожелания :relieved:\
		 						\nОбожаю когда меня хвалят как виртуального помощника :relaxed:\
		 						\nПриветствую конструктивную критику :persevere:\
		 						\nУмопомрачительно жду отзывы по улучшению работы студии :heart_eyes:\
		 						\nКак говорил :rocket: Ю.А.Гагарин - Поехали!!! :rocket:'))
		await FSMfedback.feedback_text.set()

	elif call.data == 'feed_back_no':
		async with state.proxy() as data:
			data['chat_id'] = int(call.from_user.id)
		try:
			read = gs.read_sheet(feedback_sheet_id)
			for id_chat in range(0, len(read), 1):
				if data['chat_id'] == int(read[id_chat][0]):
					row = id_chat + 2
					feedback_sheet = f"Clients!H{row}:H"
					value = [['Не захотел оставлять отзыв']]
					gs.updateRangeValues(feedback_sheet, value)
			await bot.send_message(call.from_user.id, text=emojize('Мы все равно Вас любим :kissing_heart: \
													\nПомогите нам стать чуточку лучше, обещаем мы исправимся :sob:')
			)
		except Exception as ex:
			print(ex)

async def feedback_record(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['feedback_text'] = message.text
	async with state.proxy() as data:
		data['chat_id'] = int(message.from_user.id)
	try:
		read = gs.read_sheet(feedback_sheet_id )
		for id_chat in range(0, len(read), 1):
			if data['chat_id'] == int(read[id_chat][0]):
				row = id_chat + 2
				feedback_sheet = f"Clients!H{row}:H" 
				value = [[data['feedback_text']]]
				gs.updateRangeValues(feedback_sheet, value)
		await bot.send_message(message.from_user.id, text=emojize('Спасибо я всё записал :sleeping::sweat_smile:, хорошего Вам дня :sunglasses:!!!\
																P.S.Ваш Hygge :blush:'))
		await state.finish()
	except Exception as ex:
			print(ex)

async def cancel_FSM(message: types.Message, state: FSMContext):
		curent_state = await state.get_state()
		if curent_state is None:
			return
		await state.finish()

def register_handlers_client(dp : dp):
	dp.register_message_handler(command_start, commands=['start'])
	dp.register_message_handler(cancel_FSM, state="*", commands='start')
	dp.register_message_handler(command_start, Text(equals='start', ignore_case=True), state="*")
	dp.register_callback_query_handler(start_view, text_contains='start')
	dp.register_callback_query_handler(confirm_pay, text_contains='cancel')
	dp.register_callback_query_handler(feedback_start, text_contains='feed_back')
	dp.register_message_handler(feedback_record, state=FSMfedback.feedback_text)
	dp.register_callback_query_handler(select_place, text_contains='', state='*')
	dp.register_message_handler(cl_name, state=FSMclient.name)
	dp.register_message_handler(cl_phone, state=FSMclient.phone)
	# dp.register_callback_query_handler(payments, text='btnpay')
	# dp.register_pre_checkout_query_handler(onpay)
	# dp.register_message_handler(process_pay, content_types=ContentType.SUCCESSFUL_PAYMENT)
	
	
