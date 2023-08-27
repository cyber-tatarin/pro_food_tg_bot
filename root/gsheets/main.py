import os.path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pygsheets
import asyncio

from root.logger.config import logger

logger = logger
key_json = os.path.abspath(os.path.join('root', 'gsheets', 'gsheets_key.json'))

print(key_json)


def find_row_number(user_id, worksheet):
    try:
        # Authenticate using service account credentials
        # gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        # sheet = gc.open('FERC telegram bot overview')
        # worksheet = sheet[0]
        
        cells_list_of_lists = worksheet.find(str(user_id), matchEntireCell=True)  # [[]]
        if cells_list_of_lists:  # empty list object considered as false
            return cells_list_of_lists[0].row
        else:
            return None
    except Exception as x:
        logger.exception(x)


worksheet_indexes_by_roles = {
    'loyalty_user': 0,
    'outsource_user': 1,
    'newbie': 4
}


def register_user(dict_with_kwargs: dict):
    try:
        user_id = dict_with_kwargs.get('user_id')
        user_full_name = dict_with_kwargs.get('user_full_name')
        username = f"@{dict_with_kwargs.get('username')}"
        user_role = dict_with_kwargs.get('user_role')
        
        # Authenticate using service account credentials
        gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        sheet = gc.open('FERC telegram bot overview')
        # Select the first worksheet in the Google Sheet
        worksheet_index = worksheet_indexes_by_roles.get(user_role)
        worksheet = sheet[worksheet_index]
        
        now = datetime.now()
        epoch = datetime(1899, 12, 30)
        delta = now - epoch
        current_time = delta.days + (delta.seconds / 86400)
        
        row_number = find_row_number(user_id, worksheet)
        
        if row_number is None:
            id_user_time = [[user_id, user_full_name, username, current_time]]
            
            last_row = worksheet.get_col(1, include_empty=False)
            # get the index of the first empty row
            insert_index = len(last_row)
            worksheet.insert_rows(row=insert_index, values=id_user_time, inherit=True)
        
        else:
            col_index = 4
            # Get the cell object for the specific column and edit its value
            worksheet.update_value((row_number, col_index), current_time)
    
    except Exception as x:
        logger.exception(x)


def set_loayalty_user_direction(dict_with_kwargs: dict):
    try:
        user_id = dict_with_kwargs.get('user_id')
        user_direction = dict_with_kwargs.get('user_direction')
        
        # Authenticate using service account credentials
        gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        sheet = gc.open('FERC telegram bot overview')
        # Select the first worksheet in the Google Sheet
        worksheet = sheet[0]
        
        row_number = find_row_number(user_id, worksheet)
        
        if row_number is not None:
            col_index = 5
            worksheet.update_value((row_number, col_index), user_direction)
    
    except Exception as x:
        logger.exception(x)


def set_loyalty_user_has_project(dict_with_kwargs: dict):
    try:
        user_id = dict_with_kwargs.get('user_id')
        has_project = dict_with_kwargs.get('has_project')
        
        # Authenticate using service account credentials
        gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        sheet = gc.open('FERC telegram bot overview')
        # Select the first worksheet in the Google Sheet
        worksheet = sheet[0]
        
        row_number = find_row_number(user_id, worksheet)
        
        if row_number is not None:
            has_project_col_index = 6
            num_of_projects_col_index = 7
            if has_project:
                worksheet.update_value((row_number, has_project_col_index), 'да')
            else:
                worksheet.update_value((row_number, has_project_col_index), 'нет')
            num_of_projects = worksheet.get_value((row_number, num_of_projects_col_index))
            if num_of_projects is None or num_of_projects == '':
                worksheet.update_value((row_number, num_of_projects_col_index), 0)
    
    except Exception as x:
        logger.exception(x)


def set_loyalty_user_phone_number(dict_with_kwargs: dict):
    try:
        user_id = dict_with_kwargs.get('user_id')
        phone_number = dict_with_kwargs.get('phone_number')
        
        # Authenticate using service account credentials
        gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        sheet = gc.open('FERC telegram bot overview')
        # Select the first worksheet in the Google Sheet
        worksheet = sheet[0]
        
        row_number = find_row_number(user_id, worksheet)
        
        if row_number is not None:
            col_index = 8
            worksheet.update_value((row_number, col_index), phone_number)
    
    except Exception as x:
        logger.exception(x)


def loyalty_user_submitted_project(dict_with_kwargs: dict):
    try:
        user_id = dict_with_kwargs.get('user_id')
        
        # Authenticate using service account credentials
        gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        sheet = gc.open('FERC telegram bot overview')
        # Select the first worksheet in the Google Sheet
        worksheet = sheet[0]
        
        row_number = find_row_number(user_id, worksheet)
        
        if row_number is not None:
            num_of_projects_col_index = 5
            
            num_of_projects = worksheet.get_value((row_number, num_of_projects_col_index))
            if num_of_projects is not None and num_of_projects != '':
                worksheet.update_value((row_number, num_of_projects_col_index), int(num_of_projects) + 1)
            else:
                worksheet.update_value((row_number, num_of_projects_col_index), 1)
    
    except Exception as x:
        logger.exception(x)


def outsourse_user_submitted_gform(dict_with_kwargs: dict):
    try:
        user_id = dict_with_kwargs.get('user_id')
        
        # Authenticate using service account credentials
        gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        sheet = gc.open('FERC telegram bot overview')
        # Select the first worksheet in the Google Sheet
        worksheet = sheet[1]
        
        now = datetime.now()
        epoch = datetime(1899, 12, 30)
        delta = now - epoch
        current_time = delta.days + (delta.seconds / 86400)
        
        row_number = find_row_number(user_id, worksheet)
        
        if row_number is not None:
            col_index = 5
            worksheet.update_value((row_number, col_index), current_time)
    
    except Exception as x:
        logger.exception(x)


def loyalty_user_set_remind_date(dict_with_kwargs: dict):
    try:
        user_id = dict_with_kwargs.get('user_id')
        date_str = dict_with_kwargs.get('date')
        
        # Authenticate using service account credentials
        gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        sheet = gc.open('FERC telegram bot overview')
        # Select the first worksheet in the Google Sheet
        worksheet = sheet[0]
        
        row_number = find_row_number(user_id, worksheet)
        
        if row_number is not None:
            col_index = 9
            worksheet.update_value((row_number, col_index), date_str)
    
    except Exception as x:
        logger.exception(x)


def outsource_user_set_remind_date(dict_with_kwargs: dict):
    try:
        user_id = dict_with_kwargs.get('user_id')
        date_str = dict_with_kwargs.get('date')
        
        # Authenticate using service account credentials
        gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        sheet = gc.open('FERC telegram bot overview')
        # Select the first worksheet in the Google Sheet
        worksheet = sheet[1]
        
        row_number = find_row_number(user_id, worksheet)

        if row_number is not None:
            col_index = 6
            worksheet.update_value((row_number, col_index), date_str)
    
    except Exception as x:
        logger.exception(x)


async def async_execute_of_sync_gsheets(func, **kwargs):
    executor = ThreadPoolExecutor(max_workers=10)
    loop = asyncio.get_running_loop()
    try:
        # run the blocking sync operation in a separate thread
        await loop.run_in_executor(executor, func, kwargs)
    except Exception as x:
        logger.exception(x)
    finally:
        executor.shutdown(wait=True)


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.create_task(async_execute_of_sync_gsheets(register_loyalty_user(user_id=8, username=7, user_full_name=7)))
    pass
