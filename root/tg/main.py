import asyncio
from datetime import datetime
import os
import re

from aiogram.fsm.storage.base import StorageKey
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.exc import IntegrityError

from aiogram import Bot, Dispatcher, types
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramNotFound
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram import F

from . import callback_data_models, utils, keyboards, texts
from root.db import models
from root.db import setup as db
from root.gsheets import main as gsh
from root.logger.config import logger

# конфигурация
# -------------------------------------------------------------------------------------------------

load_dotenv(find_dotenv())
bot = Bot(token=os.getenv('TG_API'))
storage = RedisStorage.from_url('redis://localhost:6379/0')
dp = Dispatcher(storage=storage)
admin_ids = {459471362, 983672566}


# -------------------------------------------------------------------------------------------------


# состояния
# -------------------------------------------------------------------------------------------------

class UserStates(StatesGroup):
    get_user_age = State()
    get_user_weight = State()
    get_user_height = State()
    get_user_weight_aim = State()


# -------------------------------------------------------------------------------------------------


# хендлеры
# -------------------------------------------------------------------------------------------------

@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer(texts.start_message, reply_markup=keyboards.get_ikb_to_get_user_start_data())
    
    session = db.Session()
    try:
        new_user = models.User(tg_id=message.from_user.id, username=message.from_user.username)
        session.add(new_user)
        session.commit()
    except IntegrityError:
        pass
    except Exception as x:
        logger.exception(x)
        await message.answer(texts.db_error_message)
    finally:
        if session.is_active:
            session.close()
            

@dp.message(Command('admin'), F.from_user.id.in_(admin_ids))
async def admin(message: types.Message):
    await message.answer('Панель администратора', reply_markup=keyboards.get_admin_ikb())


@dp.callback_query(F.data == 'get_user_start_data')
async def get_user_start_data(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer('Введите, пожалуйста, Вашу дату рождения в формате "31.12.1999"')
    await state.set_state(UserStates.get_user_age)
    await callback_query.answer()


@dp.message(UserStates.get_user_age)
async def get_user_birth_date(message: types.Message, state: FSMContext):
    if utils.is_valid_birth_date(message.text):
        await state.update_data(birth_date=message.text)
        
        await message.answer('Введите, пожалуйста, Ваш вес в килограммах в формате "72.0"')
        await state.set_state(UserStates.get_user_weight)
    else:
        await message.answer('Вы ввели некорректную дату. Пожалуйста, введите дату рождения в формате 31.12.1999')


@dp.message(UserStates.get_user_weight)
async def get_user_weight(message: types.Message, state: FSMContext):
    if utils.is_valid_weight(message.text):
        await state.update_data(weight=message.text)
        
        await message.answer('Введите, пожалуйста, Ваш рост:')
        await state.set_state(UserStates.get_user_height)
    else:
        await message.answer('Вы ввели некорректный вес. Пожалуйста, введите вес в килограммах формате "72.0", '
                             'обязательно с числом после точки')


@dp.message(UserStates.get_user_height)
async def get_user_height(message: types.Message, state: FSMContext):
    if utils.is_valid_height(message.text):
        await state.update_data(height=message.text)
        
        await message.answer('Введите, пожалуйста, Вашу цель по весу в килограммах в формате "72.0"')
        await state.set_state(UserStates.get_user_weight_aim)


@dp.message(UserStates.get_user_weight_aim)
async def get_user_weight_aim(message: types.Message, state: FSMContext):
    if utils.is_valid_weight(message.text):
        await state.update_data(weight_aim=message.text)
        
        await message.answer('Выберите, пожалуйста, уровень Вашей активности',
                             reply_markup=keyboards.get_ikb_to_choose_activity_level())
    
    else:
        await message.answer('Вы ввели некорректную цель по весу. Пожалуйста, введите Вашу цель по весу в килограммах '
                             'формате "72.0", обязательно с числом после точки')


@dp.callback_query(callback_data_models.ActivityLevelCallback.filter())
async def get_activity_level(callback_query: CallbackQuery, callback_data: callback_data_models.ActivityLevelCallback,
                             state: FSMContext):
    await state.update_data(activity_level_index=callback_data.index)
    await callback_query.message.answer('Выберите Ваш пол', reply_markup=keyboards.get_ikb_to_choose_gender())
    await callback_query.answer()


@dp.callback_query(callback_data_models.ChooseGenderCallback.filter())
async def get_gender(callback_query: CallbackQuery,
                     callback_data: callback_data_models.ChooseGenderCallback,
                     state: FSMContext):
    
    data = await state.get_data()
    print(data)
    try:
        birth_date = data['birth_date']
        weight = data['weight']
        height = data['height']
        weight_aim = data['weight_aim']
        activity_level_index = data['activity_level_index']
        gender_additional_value = callback_data.additional_value
        gender = callback_data.gender
        
        age = utils.get_age_from_birth_date(birth_date)

        calories, proteins, fats, carbohydrates, vegetables, plate_diameter = utils.count_cpfc(age, weight, height,
                                                                                               weight_aim,
                                                                                               activity_level_index,
                                                                                               gender_additional_value,
                                                                                               gender)
        birth_date = utils.str_date_to_strp(birth_date)
        session = db.Session()
        try:
            new_user = models.User(
                tg_id=callback_query.from_user.id,
                username=callback_query.from_user.username,
                birth_date=birth_date,
                height=height,
                gender=gender,
                weight_aim=weight_aim,
                plate_diameter=plate_diameter,
                day_calories=calories,
                day_proteins=proteins,
                day_fats=fats,
                day_carbohydrates=carbohydrates
            )
            session.add(new_user)
            new_measure = models.BodyMeasure(
                tg_id=callback_query.from_user.id,
                weight=weight
            )
            session.add(new_measure)
            session.commit()
        except Exception as x:
            print(x)
            await callback_query.message.answer(texts.db_error_message)
            return
        finally:
            if session.is_active:
                session.close()
        
        await callback_query.message.answer(f'{calories}, {proteins}, {fats}, {carbohydrates}, {vegetables}, '
                                            f'{plate_diameter}')
        await state.clear()
        await callback_query.answer()
        
    except KeyError as x:
        print(x)
        await callback_query.message.answer('Извините, мы потеряли Ваши данные. Введите их еще раз, пожалуйста. '
                                            'Это не займет больше 30 секунд',
                                            reply_markup=keyboards.get_ikb_to_get_user_start_data())


# -------------------------------------------------------------------------------------------------

# @dp.message(Command('manually'))
# async def states(message: types.Message, state: FSMContext):
#     await message.answer('стейт руками выставлен')
#     await storage.set_state(key=StorageKey(bot_id=bot.id, chat_id=message.from_user.id,
#                                            user_id=message.from_user.id), state='UserStates:state1')
#
#
# @dp.message(UserStates.state1)
# async def states(message: types.Message, state: FSMContext):
#     await message.answer('here we go')
#     # await storage.set_state(key=StorageKey(bot_id=bot.id, chat_id=message.from_user.id,
#     #                                        user_id=message.from_user.id), state='UserStates:state1')
#     await state.clear()


async def send_message_to_users_manually(user_ids_list: list, message):
    for user_id in user_ids_list:
        try:
            await bot.send_message(user_id, message)
            logger.info(f'message is sent to {user_id}')
        except TelegramNotFound as x:
            logger.exception(x)
        except Exception as x:
            logger.exception(x)
        finally:
            await asyncio.sleep(0.036)


if __name__ == '__main__':
    with logger.catch():
        asyncio.run(dp.start_polling(bot))
