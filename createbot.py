from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

storage = MemoryStorage()
load_dotenv()
bot = Bot(token='TOKEN')
dp = Dispatcher(bot, storage=storage)
