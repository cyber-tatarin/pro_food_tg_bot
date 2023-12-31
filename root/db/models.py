from datetime import datetime

from sqlalchemy import Column, String, Boolean, Date, Integer, DateTime, ForeignKey, Float, Text, UniqueConstraint, \
    Table
from sqlalchemy.orm import DeclarativeBase, relationship

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    tg_id = Column(Integer, primary_key=True)
    username = Column(String(100))
    date_registered = Column(DateTime, default=datetime.now)
    
    is_new = Column(Boolean, default=True)
    
    birth_date = Column(DateTime)
    height = Column(Integer)
    gender = Column(String(20))
    weight_aim = Column(Float)
    
    plate_diameter = Column(Integer)
    balance = Column(Integer, default=0)
    
    day_calories = Column(Integer)
    day_proteins = Column(Integer)
    day_fats = Column(Integer)
    day_carbohydrates = Column(Integer)
    

class BodyMeasure(Base):
    __tablename__ = 'body_measures'
    
    tg_id = Column(Integer, primary_key=True)
    date = Column(Date, default=datetime.now, primary_key=True)
    
    weight = Column(Float)
    chest_volume = Column(Integer)
    underchest_volume = Column(Integer)
    waist_volume = Column(Integer)
    belly_volume = Column(Integer)
    hips_volume = Column(Integer)


meal_ingredients_association = Table(
    'meal_ingredients_association',
    Base.metadata,
    Column('ingredient_id', Integer, ForeignKey('ingredients.ingredient_id')),
    Column('meal_id', Integer, ForeignKey('meals.meal_id')),
    Column('amount', Float, nullable=False),
    UniqueConstraint('ingredient_id', 'meal_id', 'amount', name='unique_meal_ingredients')
)

plate_meals_association = Table(
    'plate_meals_association',
    Base.metadata,
    Column('plate_id', Integer, ForeignKey('plates.plate_id')),
    Column('meal_id', Integer, ForeignKey('meals.meal_id')),
    Column('percentage', Float, nullable=False),
    UniqueConstraint('plate_id', 'meal_id', 'percentage', name='unique_plate_meals')
)

    
class Ingredient(Base):
    __tablename__ = 'ingredients'
    
    ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_name = Column(String(256), unique=True)
    
    measure = Column(String(50))
    calories = Column(Float)
    proteins = Column(Float)
    fats = Column(Float)
    carbohydrates = Column(Float)

    meals = relationship("Meal", secondary=meal_ingredients_association, back_populates="ingredients")
    
    
class Meal(Base):
    __tablename__ = 'meals'
    
    meal_id = Column(Integer, primary_key=True, autoincrement=True)
    meal_name = Column(String(120), unique=True)

    recipe = Column(Text)
    
    recipe_active_time = Column(Integer)
    recipe_time = Column(Integer)
    
    recipe_difficulty = Column(Integer)
    
    ingredients = relationship("Ingredient", secondary=meal_ingredients_association, back_populates="meals")
    plates = relationship("Plate", secondary=plate_meals_association, back_populates="meals")


class Plate(Base):
    __tablename__ = "plates"
    
    plate_id = Column(Integer, primary_key=True, autoincrement=True)
    plate_name = Column(String(120), unique=True)
    plate_type = Column(String(30))
    
    meals = relationship("Meal", secondary=plate_meals_association, back_populates="plates")
    

def date_time_to_date(context):
    return context.current_parameters['date_time'].date()


class HasEaten(Base):
    __tablename__ = "has_eaten"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    plate_id = Column(Integer)
    tg_id = Column(Integer)
    date_time = Column(DateTime, default=datetime.now)
    plate_type = Column(String(30))
    date = Column(Date, default=date_time_to_date)
    
    calories = Column(Integer, nullable=False)
    proteins = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    carbohydrates = Column(Integer, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('tg_id', 'plate_type', 'date', name='unique_eaten_user_plate_type_date'),
    )
    
    
class UserPlatesDate(Base):
    __tablename__ = "user_plates_date"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    tg_id = Column(Integer)
    plate_id = Column(Integer)
    plate_type = Column(String(30))
    date = Column(Date, default=datetime.now)
    
    __table_args__ = (
        UniqueConstraint('tg_id', 'plate_type', 'date', name='unique_user_plate_type_date'),
    )
    
    
class Favorites(Base):
    __tablename__ = "favorites"
    
    tg_id = Column(Integer, primary_key=True)
    plate_id = Column(Integer, primary_key=True)
    

class UserStreak(Base):
    __tablename__ = "user_streaks"
    
    tg_id = Column(Integer, primary_key=True)
    streak = Column(Integer)
    last_updated = Column(Date, onupdate=datetime.now)
    

class PlateReview(Base):
    __tablename__ = "plate_reviews"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer)
    plate_id = Column(Integer)
    mark = Column(Integer)
    date = Column(Date, default=datetime.now)
    
    
# class UserActionsLog(Base):
#     __tablename__ = "user_actions_log"
#
#     tg_id = Column(Integer)
#     action_type = Column(String(200))
#     date_time = Column(DateTime, default=datetime.now)
    
    
    
    
    
    
# class PlateNutrientsInfo(Base):
#     __tablename__ = "plate_nutrients_info"
#
#     plate_id = Column(Integer, primary_key=True)
#     calories = Column(Integer)
#     proteins = Column(Integer)
#     fats = Column(Integer)
#     carbohydrates = Column(Integer)

    
    