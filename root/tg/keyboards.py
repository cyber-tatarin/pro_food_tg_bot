import os

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo

from . import callback_data_models
from root.logger.config import logger
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


def get_ikb_to_get_user_start_data():
    ikbb = InlineKeyboardBuilder()
    ikbb.button(text='Ввести данные', callback_data='get_user_start_data')
    ikbb.adjust(1)
    return ikbb.as_markup()


def get_ikb_to_choose_day_ration():
    ikbb = InlineKeyboardBuilder()
    ikbb.add(InlineKeyboardButton(text='Составить рацион',
                                  web_app=WebAppInfo(url='https://9460-185-203-155-44.ngrok-free.app')))
    return ikbb.as_markup()


def get_ikb_to_choose_activity_level():
    ikbb = InlineKeyboardBuilder()
    ikbb.add(
        InlineKeyboardButton(text='Каждый день 5-10 тыс. шагов',
                             callback_data=callback_data_models.ActivityLevelCallback(index=1.2).pack()),
        InlineKeyboardButton(text='Каждый день 10-15 тыс. + 2 легкие тренировки в неделю',
                             callback_data=callback_data_models.ActivityLevelCallback(index=1.375).pack()),
        InlineKeyboardButton(text='Каждый день 8-12 тыс. шагов + 3 силовые  тренировки в неделю',
                             callback_data=callback_data_models.ActivityLevelCallback(index=1.55).pack()),
        InlineKeyboardButton(text='Каждый день 10 тыс. шагов + силовые тренировки + бытовая активность',
                             callback_data=callback_data_models.ActivityLevelCallback(index=1.725).pack()),
        InlineKeyboardButton(text='Профессиональный спортсмен',
                             callback_data=callback_data_models.ActivityLevelCallback(index=1.9).pack()),
    )
    
    ikbb.adjust(1)
    return ikbb.as_markup()


def get_ikb_to_choose_gender():
    ikbb = InlineKeyboardBuilder()
    ikbb.add(
        InlineKeyboardButton(text='Мужчина',
                             callback_data=callback_data_models.ChooseGenderCallback(additional_value=5,
                                                                                     gender='Мужчина').pack()),
        InlineKeyboardButton(text='Женщина',
                             callback_data=callback_data_models.ChooseGenderCallback(additional_value=-161,
                                                                                     gender='Женщина').pack()),
    )
    
    ikbb.adjust(1)
    return ikbb.as_markup()


web_app_link = os.getenv('WEB_APP_LINK')


def get_admin_ikb():
    ikbb = InlineKeyboardBuilder()
    ikbb.add(InlineKeyboardButton(text='Добавить ингредиент',
                                  web_app=WebAppInfo(url=f'{web_app_link}/add_ingredient')))
    ikbb.add(InlineKeyboardButton(text='Добавить блюдо',
                                  web_app=WebAppInfo(url=f'{web_app_link}/add_meal')))
    ikbb.add(InlineKeyboardButton(text='Добавить тарелку',
                                  web_app=WebAppInfo(url=f'{web_app_link}/add_plate')))

    ikbb.adjust(1)
    return ikbb.as_markup()


def get_main_view_ikb():
    ikbb = InlineKeyboardBuilder()
    ikbb.add(InlineKeyboardButton(text='Открыть профиль', web_app=WebAppInfo(url=f'{web_app_link}/main')))
    return ikbb.as_markup()


def get_choose_plates_ikb():
    ikbb = InlineKeyboardBuilder()
    ikbb.add(InlineKeyboardButton(text='Выбрать', web_app=WebAppInfo(url=f'{web_app_link}/choose_breakfast')))
    return ikbb.as_markup()
    
    
    



