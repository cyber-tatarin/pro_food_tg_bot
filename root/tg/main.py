import asyncio
import uuid
from datetime import datetime
import os
import math

from aiogram.fsm.storage.base import StorageKey
from dotenv import load_dotenv, find_dotenv

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
admin_ids = {459471362, 983672566, 617595364, 645900005}
# ADMIN_ID = 645900005
ADMIN_ID = 459471362


# -------------------------------------------------------------------------------------------------


# состояния
# -------------------------------------------------------------------------------------------------

class UserStates(StatesGroup):
    get_user_age = State()
    get_user_weight = State()
    get_user_height = State()
    get_user_weight_aim = State()
    get_user_question = State()
    answer_user_question = State()
    get_have_eaten = State()


class GetMeasuresState(StatesGroup):
    get_weight = State()
    get_chest_volume = State()
    get_underchest_volume = State()
    get_waist_volume = State()
    get_belly_volume = State()
    get_hips_volume = State()


# -------------------------------------------------------------------------------------------------


# хендлеры
# -------------------------------------------------------------------------------------------------

@dp.message(Command('start'))
async def start(message: types.Message):
    await bot.copy_message(chat_id=message.from_user.id, from_chat_id=ADMIN_ID,
                           message_id=1139, caption=texts.start_video_caption)
    await asyncio.sleep(15)
    await message.answer(texts.start_message, reply_markup=keyboards.get_ikb_to_get_user_start_data())
    
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(gsh.async_execute_of_sync_gsheets(gsh.register_user, user_id=message.from_user.id,
                                                             username=message.from_user.username,
                                                             user_full_name=message.from_user.full_name))


@dp.message(Command('admin'), F.from_user.id.in_(admin_ids))
async def admin(message: types.Message):
    await message.answer('Панель администратора', reply_markup=keyboards.get_admin_ikb())


@dp.message(Command('profile'))
async def admin(message: types.Message):
    await message.answer('Профиль', reply_markup=keyboards.get_main_view_ikb())


@dp.message(Command('choose'))
async def admin(message: types.Message):
    await message.answer('Составить рацион', reply_markup=keyboards.get_choose_plates_ikb())


@dp.callback_query(F.data == 'get_user_start_data')
async def get_user_start_data(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer('Введите, пожалуйста, Вашу дату рождения в формате "31.12.1999"')
    await state.set_state(UserStates.get_user_age)
    
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup=None)


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
        
        await message.answer('Введите, пожалуйста, Ваш рост в сантиметрах в формате "173"')
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
    else:
        await message.answer('Вы ввели некорректный рост. Пожалуйста, введите рост в сантиметрах формате "173"')


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
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dp.callback_query(callback_data_models.ChooseGenderCallback.filter())
async def get_gender(callback_query: CallbackQuery,
                     callback_data: callback_data_models.ChooseGenderCallback,
                     state: FSMContext):
    data = await state.get_data()
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
            await session.commit()
        except Exception as x:
            logger.exception(x)
            await callback_query.message.answer(texts.db_error_message)
            return
        finally:
            if session.is_active:
                await session.close()
        
        await callback_query.message.answer(f'Отлично! Мы успешно занесли все твои данные в базу. '
                                            f'Теперь нажми кнопку "Профиль" в левом нижнем углу, чтобы начать '
                                            f'пользоваться приложением!')
        await state.clear()
        
        await callback_query.answer()
        await callback_query.message.edit_reply_markup(reply_markup=None)
    
    except KeyError as x:
        await callback_query.message.answer('Извините, мы потеряли Ваши данные. Введите их еще раз, пожалуйста. '
                                            'Это не займет больше 30 секунд',
                                            reply_markup=keyboards.get_ikb_to_get_user_start_data())


@dp.callback_query(callback_data_models.ChooseQuestionTypeCallback.filter())
async def set_user_question_type(callback_query: CallbackQuery,
                                 callback_data: callback_data_models.ChooseQuestionTypeCallback,
                                 state: FSMContext):
    await bot.send_message(callback_query.from_user.id,
                           'Одним следующим сообщением отправьте, пожалуйста, Ваш вопрос в текстовой форме')
    await state.set_state(UserStates.get_user_question)
    await state.update_data(question_type=callback_data.type)
    
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dp.message(UserStates.get_user_question)
async def get_user_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        question_type = data['question_type']
    except KeyError:
        return
    
    await bot.send_message(ADMIN_ID, f'Вопрос от {message.from_user.full_name} (@{message.from_user.username})\n'
                                     f'Категория: {question_type} 👇')
    await bot.copy_message(chat_id=ADMIN_ID, from_chat_id=message.from_user.id, message_id=message.message_id,
                           reply_markup=keyboards.get_ikb_to_answer_user_question(message.from_user.id))
    await message.answer('Ваше сообщение успешно отправлено Татьяне. Вы получите ответ сообщением в этом чате')


@dp.callback_query(callback_data_models.AnswerUserQuestionCallback.filter())
async def set_state_to_answer_user_question(callback_query: CallbackQuery,
                                            callback_data: callback_data_models.AnswerUserQuestionCallback,
                                            state: FSMContext):
    await bot.send_message(ADMIN_ID,
                           f'Вы отвечаете на вопрос пользователя {callback_query.from_user.full_name} '
                           f'(@{callback_query.from_user.username}) 👇')
    
    await state.set_state(UserStates.answer_user_question)
    await state.update_data(user_id=callback_data.user_id)
    
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dp.message(UserStates.answer_user_question)
async def send_question_answer_to_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        user_id = data['user_id']
    except KeyError:
        return
    
    await bot.send_message(user_id, 'Вот ответ от Татьяны на Ваш вопрос 👇')
    await bot.copy_message(chat_id=user_id, from_chat_id=ADMIN_ID, message_id=message.message_id)
    await state.clear()
    
    # ----------------------------------------------------------------------------------------------------------


@dp.callback_query(F.data == 'start_getting_body_measures')
async def start_getting_body_measures_cb(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await bot.send_photo(callback_query.from_user.id,
                             'https://maxmaltsev-fitlife.ru/uploads/s/3/n/3/3n3j55pm3dxn/img/full_mCNbptM3.jpg',
                             caption='Это фото поможет Вам сделать замеры')
    except Exception as x:
        logger.exception(x)
    
    await asyncio.sleep(1)
    await callback_query.message.answer('Введите, пожалуйста, Ваш вес в кг на данный момент в формате "72.0"')
    await state.set_state(GetMeasuresState.get_weight)
    
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dp.message(GetMeasuresState.get_weight)
async def get_weight(message: types.Message, state: FSMContext):
    if utils.is_valid_weight(message.text):
        await message.answer('Введите, пожалуйста, Ваш объем груди в см в формате "90"')
        await state.set_state(GetMeasuresState.get_chest_volume)
        await state.update_data(weight=message.text)
    else:
        await message.answer('Вы ввели не число. Введите, пожалуйста, целое число')


@dp.message(GetMeasuresState.get_chest_volume)
async def get_chest_volume(message: types.Message, state: FSMContext):
    if message.text.isdecimal():
        await message.answer('Введите, пожалуйста, Ваш объем под грудью в см в формате "70"')
        await state.set_state(GetMeasuresState.get_underchest_volume)
        await state.update_data(chest_volume=message.text)
    else:
        await message.answer('Вы ввели не число. Введите, пожалуйста, целое число')


@dp.message(GetMeasuresState.get_underchest_volume)
async def get_under_chest_volume(message: types.Message, state: FSMContext):
    if message.text.isdecimal():
        await message.answer('Введите, пожалуйста, Ваш объем талии в см в формате "75"')
        await state.set_state(GetMeasuresState.get_waist_volume)
        await state.update_data(underchest_volume=message.text)
    else:
        await message.answer('Вы ввели не число. Введите, пожалуйста, целое число')


@dp.message(GetMeasuresState.get_waist_volume)
async def get_waist_volume(message: types.Message, state: FSMContext):
    if message.text.isdecimal():
        await message.answer('Введите, пожалуйста, Ваш объем живота в см в формате "80"')
        await state.set_state(GetMeasuresState.get_belly_volume)
        await state.update_data(waist_volume=message.text)
    else:
        await message.answer('Вы ввели не число. Введите, пожалуйста, целое число')


@dp.message(GetMeasuresState.get_belly_volume)
async def get_belly_volume(message: types.Message, state: FSMContext):
    if message.text.isdecimal():
        await message.answer('Введите, пожалуйста, Ваш объем бёдер см в формате "90"')
        await state.set_state(GetMeasuresState.get_hips_volume)
        await state.update_data(belly_volume=message.text)
    else:
        await message.answer('Вы ввели не число. Введите, пожалуйста, целое число')


@dp.message(GetMeasuresState.get_hips_volume)
async def get_hips_volume(message: types.Message, state: FSMContext):
    if message.text.isdecimal():
        data = await state.get_data()
        try:
            weight = data['weight']
            chest_volume = data['chest_volume']
            underchest_volume = data['underchest_volume']
            waist_volume = data['waist_volume']
            belly_volume = data['belly_volume']
            hips_volume = message.text
        except KeyError:
            await message.answer('Что-то пошло не так, введите данные еще раз, пожалуйста',
                                 reply_markup=keyboards.get_ikb_to_start_getting_body_measures())
            return
        
        else:
            session = db.Session()
            try:
                new_body_measure_obj = models.BodyMeasure(tg_id=message.from_user.id,
                                                          weight=weight, chest_volume=chest_volume,
                                                          underchest_volume=underchest_volume,
                                                          waist_volume=waist_volume,
                                                          belly_volume=belly_volume, hips_volume=hips_volume)
                session.add(new_body_measure_obj)
                await session.commit()
            
            except Exception as x:
                logger.exception(x)
                await message.answer('Что-то пошло не так, введите данные еще раз, пожалуйста',
                                     reply_markup=keyboards.get_ikb_to_start_getting_body_measures())
            finally:
                if session.is_active:
                    await session.close()
        
        await message.answer('Отличо! Мы успешно занесли Ваши данные в базу. Вы можете посмотреть свою '
                             'понедельную статистику в профиле')
        await state.clear()
    
    else:
        await message.answer('Вы ввели не число. Введите, пожалуйста, целое число')


# -------------------------------------------------------------------------------------------------
@dp.message(Command('eat'))
async def store_file_ids(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.get_have_eaten)


@dp.message(UserStates.get_have_eaten, F.content_type.in_({types.ContentType.VOICE, types.ContentType.TEXT}))
async def set_have_eaten_without_plates(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.TEXT:
        have_eaten_in_text = message.text
    else:
        filename = f'{uuid.uuid4().int}.mp3'
        file_path = os.path.join('root', 'tg', 'media', filename)
        await bot.download(message.voice, file_path)
        try:
            have_eaten_in_text = await utils.speech_to_text(file_path)
        except Exception as x:
            have_eaten_in_text = None
            logger.exception(x)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    if have_eaten_in_text is not None:
        ai_response = await utils.ai_analysis(have_eaten_in_text)
        if ai_response is not None:
            try:
                calories = int(ai_response['calories'])
                proteins = int(ai_response['proteins'])
                fats = int(ai_response['fats'])
                carbohydrates = int(ai_response['carbohydrates'])
                
                session = db.Session()
                try:
                    user = await session.get(models.User, message.from_user.id)
                except Exception as x:
                    logger.exception(x)
                    await message.answer(texts.db_error_message)
                    return
                finally:
                    await session.close()
            
                await message.answer(f'Это примерно:\n\n{math.ceil(calories / user.day_calories)} % от дневной нормы ккал\n'
                                     f'{math.ceil(proteins / user.day_proteins)} % от дневной нормы белка\n'
                                     f'{math.ceil(fats / user.day_fats)} % от дневной нормы жиров\n'
                                     f'{math.ceil(carbohydrates / user.day_carbohydrates)} % от дневной нормы углеводов')
                await state.clear()
                return
            
            except KeyError:
                pass

    await message.answer('Эта функция пока недоступна, но здесь будет выводиться то, сколько процентов от '
                         'Вашего рациона составляет то, что Вы сейчас ввели:)')


# -------------------------------------------------------------------------------------------------

@dp.message(F.from_user.id.in_(admin_ids), F.content_type.in_({types.ContentType.VOICE, types.ContentType.VIDEO_NOTE, types.ContentType.VIDEO}))
async def store_file_ids(message: types.Message):
    with open(os.path.join('root', 'tg', 'admin_media_records.txt'), 'a') as file:
        file.write(f'{message.from_user.id} : {message.message_id} {message.content_type} {datetime.now()}\n\n')


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


async def get_user_question_type(user_id):
    await bot.send_message(user_id, 'Выберите категорию, к которой можно отнести Ваш вопрос',
                           reply_markup=keyboards.get_ikb_to_get_question_type())


async def start_getting_body_measures(user_id):
    await bot.send_message(user_id, 'Пришло время еженедельных замеров, которые важны, чтобы отслеживать Ваш прогресс.'
                                    '\n\nНажмите на кнопку ниже, чтобы начать! Это займет не больше 5 минут',
                           reply_markup=keyboards.get_ikb_to_start_getting_body_measures())


async def get_has_eaten_without_plates(user_id):
    await bot.send_message(user_id, 'Пришлите, пожалуйста то, что Вы съели в свободной форме в виде текста '
                                    'или голосового сообщения')
    await storage.set_state(key=StorageKey(bot_id=bot.id, chat_id=user_id,
                                           user_id=user_id), state='UserStates:get_have_eaten')


async def what_else_to_eat(user_id):
    await bot.copy_message(chat_id=user_id, from_chat_id=ADMIN_ID, message_id=1039)


async def send_breakfast_notification(user_id):
    await bot.send_message(user_id, 'Доброе утро, пора составлять рацион и завтракать!')


async def send_lunch_notification(user_id):
    await bot.send_message(user_id, 'Добрый день, время обеда!')


async def send_dinner_notification(user_id):
    await bot.send_message(user_id, 'Добрый вечер, не забудьте поужинать и отметить!')


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
