import schedule
import asyncio
from root.db import setup as db, models
from root.logger.config import logger
from datetime import datetime, date
from sqlalchemy import func, select
from root.tg.main import start_getting_body_measures, send_breakfast_notification, \
    send_lunch_notification, send_dinner_notification


async def set_user_streak_to_0_if_was_not_active_today():
    session = db.Session()
    today = date.today()
    try:
        all_user_streaks_query = await session.execute(select(models.UserStreak))
        all_user_streaks = all_user_streaks_query.scalars().all()
        for user_streak_obj in all_user_streaks:
            last_updated = user_streak_obj.last_updated
            if last_updated:
                if last_updated < today:
                    user_streak_obj.streak = 0
                    
        await session.commit()
    
    except Exception as x:
        logger.exception(x)
    finally:
        if session.is_active:
            await session.close()


async def get_body_measures():
    session = db.Session()
    try:
        users_query = await session.execute(select(models.User))
        users = users_query.scalars().all()
        # users = session.query(models.User).filter(models.User.tg_id == 459471362).all()
        for user in users:
            try:
                await start_getting_body_measures(user.tg_id)
            except Exception as x:
                logger.exception(x)
                
            await asyncio.sleep(0.04)
    except Exception as x:
        logger.exception(x)
    finally:
        if session.is_active:
            await session.close()


async def activate_func_for_all_users(exec_func):
    session = db.Session()
    try:
        users_query = await session.execute(select(models.User))
        users = users_query.scalars().all()
        # users = session.query(models.User).filter(models.User.tg_id == 459471362).all()
        for user in users:
            try:
                await exec_func(user.tg_id)
            except Exception as x:
                logger.exception(x)
            
            await asyncio.sleep(0.04)
    except Exception as x:
        logger.exception(x)
    finally:
        if session.is_active:
            await session.close()
            

def set_user_streak_to_0_if_was_not_active_today_job():
    asyncio.create_task(set_user_streak_to_0_if_was_not_active_today())
    
    
def get_body_measures_job():
    asyncio.create_task(activate_func_for_all_users(start_getting_body_measures))
    
    
def send_breakfast_notification_job():
    asyncio.create_task(activate_func_for_all_users(send_breakfast_notification))
    
    
def send_lunch_notification_job():
    asyncio.create_task(activate_func_for_all_users(send_lunch_notification))
    
    
def send_dinner_notification_job():
    asyncio.create_task(activate_func_for_all_users(send_dinner_notification))


# Schedule the job to run every day at 10 pm
schedule.every().day.at("23:55").do(set_user_streak_to_0_if_was_not_active_today_job)
schedule.every().saturday.at("19:00").do(get_body_measures_job)

schedule.every().day.at("08:30").do(send_breakfast_notification_job)
schedule.every().day.at("14:30").do(send_lunch_notification_job)
schedule.every().day.at("19:30").do(send_dinner_notification_job)


async def run_schedule():
    while True:
        schedule.run_pending()
        await asyncio.sleep(40)


# Run the asyncio event loop
asyncio.run(run_schedule())
