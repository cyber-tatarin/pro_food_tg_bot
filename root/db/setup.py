import os

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
from root.db import models
from root.logger.config import logger

load_dotenv(find_dotenv())
logger = logger

engine = create_engine(
        f'{os.getenv("DB_ENGINE")}://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}',
        poolclass=pool.QueuePool, pool_size=10, max_overflow=20, pool_pre_ping=True)

Session = sessionmaker(bind=engine)

if __name__ == '__main__':
    # pass
    # models.Base.metadata.drop_all(bind=engine)
    # models.Base.metadata.create_all(bind=engine)
    
    # models.User.__table__.drop(bind=engine)
    # models.BodyMeasure.__table__.drop(bind=engine)
    # models.Ingredient.__table__.drop(bind=engine)
    # models.Meal.__table__.drop(bind=engine)
    # models.Plate.__table__.drop(bind=engine)
    # models.ingredient_measure_association.create(bind=engine)
#     #
#     models.User.__table__.create(bind=engine)
#     models.BodyMeasure.__table__.create(bind=engine)
#     models.Ingredient.__table__.create(bind=engine)
#     models.Meal.__table__.create(bind=engine)
#     models.Plate.__table__.create(bind=engine)
#     models.meal_ingredients_association.create(bind=engine)
    models.plate_meals_association.create(bind=engine)
    
    # session = Session()
    # ingredient2 = models.Ingredient(ingredient_name="Ingredient 4", proteins=1)
    # meal1 = models.Meal(meal_name="Meal 4", recipe='grgrr')
    #
    # session.add_all([ingredient2, meal1])
    #
    # session.commit()
    #
    # association = models.ingredient_measure_association.insert().values(
    #     amount=2,
    #     ingredient=ingredient2.ingredient_id,
    #     meal=meal1.meal_id
    # )
    # session.execute(association)
    # session.commit()
    # association.ingredient = ingredient2
    # association.meal = meal1
    # Create measures with unique nutritional va
    #
    # lues

    #
    # mealss = session.query(models.ingredient_measure_association).filter(models.ingredient_measure_association.c.meal == 3).all()
    # print(mealss)
