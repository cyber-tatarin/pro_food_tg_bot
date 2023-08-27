from sqlalchemy import Column, String, Boolean, Date, Integer
from sqlalchemy.orm import DeclarativeBase

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Base(DeclarativeBase):
    pass


# храним состояние о юзере, чтобы восстановить в случае отключения бота
class State(Base):
    __tablename__ = "states"
    
    tg_id = Column("tg_id", String(12), primary_key=True)
    state = Column("state", String(60))


# пользователь, которого интересует программ лояльности
# храним инфо о том, заполнил ли он форму, чтобы позже дудосить тех, кто не заполнил
class LoyaltyUser(Base):
    __tablename__ = "loyalty_users"
    
    tg_id = Column("tg_id", String(12), primary_key=True)
    direction = Column("direction", String(30), nullable=True)
    has_project = Column("has_project", Boolean, nullable=False, default=False)
    phone_number = Column("phone_number", String(14), nullable=True)
    submitted_plans = Column("submitted_plans", Integer, nullable=True, default=0)


# пользователь, который ищет доп. работу на аутсорсе
# храним инфо о том, отправил ли он план
class OutsourceUser(Base):
    __tablename__ = "outsource_users"
    
    tg_id = Column("tg_id", String(12), primary_key=True)
    has_submitted_gform = Column("has_submitted_gform", Boolean, nullable=False, default=False)


# таблица с уведомлениями на определенную дату
class Notification(Base):
    __tablename__ = "notifications"
    
    tg_id = Column("tg_id", String(12), primary_key=True)
    user_role = Column("user_role", String(12), primary_key=True)
    date = Column("date", Date)
