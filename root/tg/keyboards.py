from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo

from . import callback_data_models
from root.logger.config import logger


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


def get_admin_ikb():
    ikbb = InlineKeyboardBuilder()
    ikbb.add(InlineKeyboardButton(text='Добавить блюдо',
                                  web_app=WebAppInfo(url='https://125f-2a02-bf0-1403-c5ca-f09e-a0ed-ad32-b469.ngrok-free.app/add_meal')))
    ikbb.add(InlineKeyboardButton(text='Добавить ингредиент',
                                  web_app=WebAppInfo(url='https://125f-2a02-bf0-1403-c5ca-f09e-a0ed-ad32-b469.ngrok-free.app/add_ingredient')))
    ikbb.adjust(1)
    return ikbb.as_markup()
    
    
    



