import asyncio
import datetime
import os
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import ChatNotFound
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.exc import IntegrityError

from . import callback_data_models, utils, keyboards
from root.db import models
from root.db import setup as db
from root.gsheets import main as gsh
from root.logger.config import logger

load_dotenv(find_dotenv())

bot = Bot(os.getenv('TG_API'))
storage = MemoryStorage()

dp = Dispatcher(bot=bot, storage=storage)

MANAGER_IDS = [459471362, 1287712867, 899761612]
# MANAGER_IDS = [459471362]


async def send_message_to_users_manually(user_ids_list: list, message):
    for user_id in user_ids_list:
        try:
            await bot.send_message(user_id, message)
            logger.info(f'message is sent to {user_id}')
        except ChatNotFound as x:
            logger.exception(x)
        except Exception as x:
            logger.exception(x)
        finally:
            await asyncio.sleep(0.036)


async def restore_user_states(_):
    session = db.Session()
    try:
        for row in session.query(models.State).all():
            await storage.set_state(user=int(row.tg_id), state=row.state, chat=int(row.tg_id))
    except Exception as x:
        logger.exception(x)
    finally:
        if session.is_active:
            session.close()


if __name__ == '__main__':
    with logger.catch():
        executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=restore_user_states)
