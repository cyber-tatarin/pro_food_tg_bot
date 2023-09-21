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


def register_user(dict_with_kwargs: dict):
    try:
        user_id = dict_with_kwargs.get('user_id')
        user_full_name = dict_with_kwargs.get('user_full_name')
        username = f"@{dict_with_kwargs.get('username')}"
        user_role = dict_with_kwargs.get('user_role')
        
        # Authenticate using service account credentials
        gc = pygsheets.authorize(service_file=key_json)
        
        # Open the Google Sheet by name
        sheet = gc.open('pro_food_tg_bot online db')
        # Select the first worksheet in the Google Sheet
        worksheet = sheet.worksheet_by_title('ingredients')
        
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
        

def add_to_sheet(sheet_name, list_of_inputs):
    # Authenticate using service account credentials
    gc = pygsheets.authorize(service_file=key_json)
    # Convert the list of links into a single column
    
    # Open the Google Sheet by name
    sheet = gc.open('pro_food_tg_bot online db')
    # Select the first worksheet in the Google Sheet
    worksheet = sheet.worksheet_by_title(sheet_name)

    worksheet.insert_rows(row=1, values=list_of_inputs)


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
    # register_user({'user_id': 2})
    new_ingredient('g0', 1, 2, 3, 4)
