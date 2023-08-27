import re

import schedule
import asyncio
from root.db import setup as db, models
from root.tg.main import bot
from root.tg import keyboards
from root.logger.config import logger
from aiogram.utils.exceptions import ChatNotFound, BotBlocked
import datetime
from sqlalchemy import func

notification_texts = {
    'loyalty': "Вы просили напомнить о нас. Если у Вас появился проект, "
               "Вы можете отправить нам его на просчёт по программе лояльности",
    'outsource': "Вы просили напомнить Вам о нас. Мы предлагаем проектировщикам дополнительную работу на аутсорсе. "
                 "Заполните, пожалуйста, гугл форму, чтобы получить проект"
}

notification_ikbs = {
    'loyalty': keyboards.get_ikb_to_get_project_or_remind_later,
    'outsource': keyboards.get_ikb_with_google_form_link
}

logger = logger


async def my_function():
    session = db.Session()
    current_date = datetime.date.today()
    try:
        all_notification_objs_for_today = session.query(models.Notification).filter(func.DATE(models.Notification.date) == current_date).all()
        if len(all_notification_objs_for_today) > 0:
            for notification_obj in all_notification_objs_for_today:
                message_text = notification_texts.get(notification_obj.user_role)
                message_ikb = notification_ikbs.get(notification_obj.user_role)
                await bot.send_message(notification_obj.tg_id, message_text,
                                       reply_markup=message_ikb(tg_id=notification_obj.tg_id))
                session.delete(notification_obj)
            session.commit()
            
    except (ChatNotFound, BotBlocked):
        pass
    
    except Exception as x:
        logger.exception(x)
        await bot.send_message(459471362, 'Проблема с уведомлениями')
        
        
def job():
    asyncio.create_task(my_function())


# Schedule the job to run every day at 10 pm
schedule.every().day.at("10:00").do(job)


async def run_schedule():
    while True:

        schedule.run_pending()
        await asyncio.sleep(1)


# Run the asyncio event loop
asyncio.run(run_schedule())
# date_pattern = r'[0123]\d\.[01]\d\.2023'
# print(re.match(date_pattern, '31.12.2023'))
