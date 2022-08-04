from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

btnadmin = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_load = KeyboardButton('Загрузить')
btn_del = KeyboardButton('Удалить') 
mailing = KeyboardButton('Рассылка')
btn_cancel = KeyboardButton('Отмена')
btnadmin.add(btn_load).add(btn_del).add(mailing).add(btn_cancel)