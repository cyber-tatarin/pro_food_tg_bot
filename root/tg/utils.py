# в этом файле лежат все функции, не связанные с приемом сообщений и запросов от пользователей

from root.db import setup as db, models
from sqlalchemy.exc import IntegrityError
from root.logger.config import logger
from root.gsheets import main as gsh
import asyncio
from aiogram.utils.exceptions import ChatNotFound
import re
from . import keyboards

logger = logger


async def save_state_into_db(user_id, state):
    session = db.Session()
    try:
        state_db_object = models.State(tg_id=user_id, state=state)
        session.add(state_db_object)
        session.commit()
    except IntegrityError:
        session.rollback()
        existing_state_object = session.query(models.State).filter(models.State.tg_id == str(user_id)).first()
        existing_state_object.state = state
    except Exception as x:
        logger.exception(x)
    finally:
        if session.is_active:
            session.close()


async def delete_state_from_db(user_id):
    session = db.Session()
    try:
        existing_state_object = session.query(models.State).filter(models.State.tg_id == str(user_id)).first()
        session.delete(existing_state_object)
        session.commit()
    except Exception as x:
        logger.exception(x)
    finally:
        if session.is_active:
            session.close()
        
            
def is_valid_phone_number(phone_number):
    patterns = [r'^\+375\d{9}$', r'^\+7\d{10}$']  # Беларусь, Россия/Казахстан
    for pattern in patterns:
        if re.match(pattern, phone_number) is not None:
            return True
    return False





        
