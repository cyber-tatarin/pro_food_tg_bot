import re

import schedule
import asyncio
from root.db import setup as db, models
from root.logger.config import logger
from datetime import datetime, date
from sqlalchemy import func


async def set_user_streak_to_0_if_was_not_active_today():
    session = db.Session()
    today = date.today()
    try:
        all_user_streaks = session.query(models.UserStreak).all()
        for user_streak_obj in all_user_streaks:
            last_updated = user_streak_obj.last_updated
            if last_updated:
                if last_updated < today:
                    user_streak_obj.streak = 0
                    
        session.commit()
    
    except Exception as x:
        logger.exception(x)
    finally:
        if session.is_active:
            session.close()


def set_user_streak_to_0_if_was_not_active_today_job():
    asyncio.create_task(set_user_streak_to_0_if_was_not_active_today())


# Schedule the job to run every day at 10 pm
schedule.every().day.at("23:55").do(set_user_streak_to_0_if_was_not_active_today_job)


async def run_schedule():
    while True:
        schedule.run_pending()
        await asyncio.sleep(40)


# Run the asyncio event loop
asyncio.run(run_schedule())
# date_pattern = r'[0123]\d\.[01]\d\.2023'
# print(re.match(date_pattern, '31.12.2023'))
