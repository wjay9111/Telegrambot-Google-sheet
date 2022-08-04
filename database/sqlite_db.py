import sqlite3 as sq
from datetime import datetime
from aiogram.types import InputMediaPhoto

dt = datetime.now().strftime("%d/%m/%Y %H:%M")

def sql_start():
	global base, cur
	base = sq.connect('database.db')
	cur = base.cursor()
	if base:
		print('Data Base connected!')
	base.execute('CREATE TABLE IF NOT EXISTS content(img TEXT, name TEXT PRIMARY KEY, description TEXT)')
	base.execute("CREATE TABLE IF NOT EXISTS pre_records(room TEXT, photograph TEXT, 'date' TEXT, 'time' TEXT, name TEXT, phone TEXT, id_chat INTEGER PRIMARY KEY)")
	base.commit()

# таблица записи клиентов
def sql_add_pre_records(val, id_chat):
		if val == None:
			val = {'room': 'Null',
					 'photograph': 'Null',
					 'date': 'Null',
					 'time': 'Null',
					 'name': 'Null',
					 'phone': 'Null',
					 'id_chat': id_chat
				   }
			print(val)
			cur.execute('INSERT INTO pre_records VALUES(?, ?, ?, ?, ?, ?, ?)',
						(
							val['room'], val['photograph'], val['date'], val['time'], val['name'], val['phone'],
							val['id_chat']))
			base.commit()
		else:
			if 'room' in val:
				cur.execute('UPDATE pre_records SET room == ? WHERE Id_chat == ?', (val['room'], id_chat))
				base.commit()
				print(f'{dt}: Update Room Successful!!!')
			else:
				print('no update Room...')

			if 'photograph' in val:
				cur.execute('UPDATE pre_records SET photograph == ? WHERE Id_chat == ?', (val['photograph'], id_chat))
				base.commit()
				print(f'{dt}: Update Photograph Successful!!!')
			else:
				print('No update Photograph...')

			if 'date' in val:
				cur.execute('UPDATE pre_records SET date == ? WHERE Id_chat == ?', (val['date'], id_chat))
				base.commit()
				print(f'{dt}: Update Date Successful!!!')
			else:
				print('No update Date...')

			if 'time' in val:
				cur.execute('UPDATE pre_records SET time == ? WHERE Id_chat == ?', (val['time'], id_chat))
				base.commit()
				print(f'{dt}: Update Time Successful!!!')
			else:
				print('No update Time...')

			if 'name' in val:
				cur.execute('UPDATE pre_records SET name == ? WHERE Id_chat == ?', (val['name'], id_chat))
				base.commit()
				print(f'{dt}: Update Name Successful!!!')
			else:
				print('No update Name...')

			if 'phone' in val:
				cur.execute('UPDATE pre_records SET phone == ? WHERE Id_chat == ?', (val['phone'], id_chat))
				base.commit()
				print(f'{dt}: Update Phone Successful!!!')
			else:
				print('No update Phone...')


def sql_read_pre_records(id_chat):
	for ret in cur.execute('SELECT * FROM pre_records WHERE id_chat=?', (id_chat,)).fetchall():
		return ret

def sql_read_pre_records_date(date):
	free_time = []
	for ret in cur.execute('SELECT * FROM pre_records WHERE `date`=?', (date, )).fetchall():
		free_time.append(ret[2])
	return free_time

async def sql_add_command(state):
	try:
		async with state.proxy() as data:
			cur.execute('INSERT INTO content VALUES (?, ?, ?)', tuple(data.values()))
			base.commit()
	except Exception as ex:
		print(ex) 

# читает базу данных и фильтрует по названию и отправляет фото логотипа
def sql_read_logo():
	try:
		logo = []
		for ret in cur.execute('SELECT * FROM content').fetchall():		
			if 'logo' in ret[1] :
				logo.append(ret[0])
				logo.append(ret[2])

				
				
	except Exception as ex:
		print(ex) 
	return logo

# читает базу данных и фильтрует по названию и отправляет фото основной рум
def sql_read_first_room():
	try:
		i = 0
		for ret in cur.execute('SELECT * FROM content').fetchall():		
			if 'oz' in ret[1] :
				if i == 0:
					group = [InputMediaPhoto(ret[0], ret[2])]
				else:
					group.append(InputMediaPhoto(ret[0]))
				i += 1
				
	
	except Exception as ex:
		print(ex) 
	return group

# читает базу данных и фильтрует по названию и отправляет фото бэйби рум
def sql_read_baby_room():
	try:
		i = 0
		for ret in cur.execute('SELECT * FROM content').fetchall():
			if 'bb' in ret[1] :
				if i == 0:
					group = [InputMediaPhoto(ret[0], ret[2])]
				else:
					group.append(InputMediaPhoto(ret[0]))
				i += 1

	except Exception as ex:
		print(ex) 
	return group

# читает базу данных и фильтрует по названию и отправляет фото оба рума	
def sql_read_rooms():
	try:
		for ret in cur.execute('SELECT * FROM content').fetchall():
			if 'ro' in ret[1] :
				group = [InputMediaPhoto(ret[0], ret[2])]			

	except Exception as ex:
		print(ex) 
	return group

def sql_read_rules():
	try:
		for ret in cur.execute('SELECT * FROM content').fetchall():
			if 'ru' in ret[1] :
				group = [InputMediaPhoto(ret[0], ret[2])]			

	except Exception as ex:
		print(ex) 
	return group

async def sql_read():
	return cur.execute('SELECT * FROM content').fetchall()

async def sql_delete_command(data):
	cur.execute('DELETE FROM content WHERE name == ?', (data,))
	base.commit()

def sql_delete_pre_records(id_chat):
	cur.execute('DELETE FROM pre_records WHERE id_chat = ?', (id_chat,))
	base.commit()