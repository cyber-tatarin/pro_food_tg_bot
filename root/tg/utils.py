# в этом файле лежат все функции, не связанные с приемом сообщений и запросов от пользователей
import os
from datetime import datetime
import assemblyai as aai

from root.db import setup as db, models
from sqlalchemy.exc import IntegrityError
from root.logger.config import logger
from root.gsheets import main as gsh
import asyncio
import re
# from . import keyboards
        
            
def is_valid_phone_number(phone_number):
    patterns = [r'^\+375\d{9}$', r'^\+7\d{10}$']  # Беларусь, Россия/Казахстан
    for pattern in patterns:
        if re.match(pattern, phone_number) is not None:
            return True
    return False


def is_valid_birth_date(birth_date_as_str: str):
    date_pattern = r'^\d{2}\.\d{2}.\d{4}$'
    
    # Use re.match to check if the string matches the pattern
    if re.match(date_pattern, birth_date_as_str):
        if 1945 < int(birth_date_as_str[-4:]) < 2020:
            return True
    return False


def is_valid_weight(weight_as_str: str):
    # Define the number pattern regex
    number_pattern = r'^\d+\.\d$'

    # Use re.match to check if the string matches the pattern
    if re.match(number_pattern, weight_as_str):
        if 35 < float(weight_as_str) < 150:
            return True
    return False


def is_valid_height(height_as_str: str):
    # Define the number pattern regex
    number_pattern = r'^\d\d\d$'

    # Use re.match to check if the string matches the pattern
    if re.match(number_pattern, height_as_str):
        if 100 < float(height_as_str) < 230:
            return True
    return False


def get_age_from_birth_date(birth_date_as_str):
    parsed_date = datetime.strptime(birth_date_as_str, "%d.%m.%Y")
    
    # Get the current date
    current_date = datetime.now()
    
    # Calculate the time difference between the current date and the parsed date
    time_difference = current_date - parsed_date
    
    # Calculate the number of full years that have passed
    age = time_difference.days // 365
    
    return age


def count_cpfc(age, weight: float, height, weight_aim: float, activity_level_index, gender_additional_value, gender):
    age = float(age)
    weight = float(weight)
    height = float(height)
    weight_aim = float(weight_aim)
    activity_level_index = float(activity_level_index)
    gender_additional_value = float(gender_additional_value)
    
    normal_cpfc = (10.0 * float(weight) + 6.25 * float(height) + 5.0 * float(age) + float(gender_additional_value)) * float(activity_level_index)
    
    weight_delta = weight_aim - weight
    if abs(weight_delta) < 2:
        proteins, fats, carbohydrates, vegetables = get_nutrients_from_calories(normal_cpfc)
        plate_diameter = determine_plate_size(normal_cpfc, gender)
        return int(normal_cpfc), proteins, fats, carbohydrates, vegetables, plate_diameter
    
    if weight_delta > 0:
        gain_cpfc = normal_cpfc + 300.0
        proteins, fats, carbohydrates, vegetables = get_nutrients_from_calories(gain_cpfc)
        plate_diameter = determine_plate_size(gain_cpfc, gender)
        return int(gain_cpfc), proteins, fats, carbohydrates, vegetables, plate_diameter
    
    else:
        loss_cpfc = normal_cpfc - 300.0
        proteins, fats, carbohydrates, vegetables = get_nutrients_from_calories(loss_cpfc)
        plate_diameter = determine_plate_size(loss_cpfc, gender)
        return int(loss_cpfc), proteins, fats, carbohydrates, vegetables, plate_diameter
    
    
def get_nutrients_from_calories(calories):
    proteins = calories * 0.35 / 4.0
    fats = calories * 0.25 / 9.0
    carbohydrates = calories * 0.3 / 4.0
    vegetables = calories * 0.1
    
    return int(proteins), int(fats), int(carbohydrates), int(vegetables)


def determine_plate_size(calories, gender):
    if gender == 'Женщина':
        if calories <= 1400:
            return 21
        # elif calories <= 1800:
        #     return '23см'
        else:
            return 23
    elif gender == 'Мужчина':
        if calories <= 1700:
            return 23
        # elif calories <= 2000:
        #     return '25см'
        else:
            return 25
    else:
        return 'Некорректный пол'


def str_date_to_strp(date_as_str):
    try:
        # Parse the date string using the specified format
        date_format = "%d.%m.%Y"
        datetime_obj = datetime.strptime(date_as_str, date_format)
        return datetime_obj
    except ValueError:
        # Handle invalid date strings
        return None
    
# print(count_cpfc(19, 72.0, 173, 80, 1.5, -161, 'Женщина'))


aai.settings.api_key = os.getenv('AAI_API_KEY')
config = aai.TranscriptionConfig(language_code="ru")
transcriber = aai.Transcriber(config=config)


def speech_to_text(audiofile_path):
    transcript = transcriber.transcribe(audiofile_path)
    return transcript.text
    





        
