import json
import os
import threading
from datetime import datetime

import aiohttp
from aiohttp import web
import jinja2
import aiohttp_jinja2
from sqlalchemy import func, select, text
from dotenv import load_dotenv, find_dotenv

from root.db import setup as db
from root.db import models
from root.logger.config import logger
from root.tg.main import admin_ids
from root.tg.utils import get_age_from_birth_date
from root.gsheets import main as gsh
from . import utils


load_dotenv(find_dotenv())


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join('root', 'web', 'templates')),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True
)


#
# @aiohttp_jinja2.template('profile_view.html')
# async def profile_view(request):
#     user_id = request.match_info.get('user_id')
#
#     pass


@aiohttp_jinja2.template('add_ingredient.html')
async def add_ingredient_get(request):
    return {}


async def add_ingredient_post(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    await utils.is_admin_by_id(tg_id)
    
    name = data.get('name')

    measure = data.get('measure')
    if measure == '' or measure is None:
        return web.json_response({'success': False, 'error_message': 'Вы не выбрали меру'})
    
    calories = data.get('calories')
    proteins = data.get('proteins')
    fats = data.get('fats')
    carbohydrates = data.get('carbohydrates')
    
    session = db.Session()
    try:
        new_ingredient = models.Ingredient(
            ingredient_name=name,
            measure=measure,
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbohydrates=carbohydrates
        )
        session.add(new_ingredient)
        session.commit()
        session.refresh(new_ingredient)
        new_ingredient_id = new_ingredient.ingredient_id

        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('ingredients',
                                                                        [[new_ingredient_id, name, measure,
                                                                          calories, proteins,
                                                                          fats, carbohydrates]]))
        gsheet_thread.start()
        
    except Exception as x:
        print(x)
        return web.json_response({'success': False,
                                  'error_message': 'Вы ввели данные некорректно, проверьте пожалуйста'})
    finally:
        if session.is_active:
            session.close()
    
    return web.json_response({'success': True})


@aiohttp_jinja2.template('add_meal.html')
async def add_meal_get(request):
    return {}


async def add_meal_post(request):
    print('Got data')
    data = await request.json()
    tg_id = data.get('tg_id')
    await utils.is_admin_by_id(tg_id)
    
    print(data)
    print('Parsed data')
    
    name = data.get('name')
    recipe = data.get('recipe')
    
    recipe_time = data.get('recipe_time')
    recipe_active_time = data.get('recipe_active_time')
    recipe_difficulty = data.get('recipe_difficulty')
    
    session1 = db.Session()
    print('Created session')
    try:
        new_meal = models.Meal(
            meal_name=name,
            recipe=recipe,
            recipe_time=recipe_time,
            recipe_difficulty=recipe_difficulty,
            recipe_active_time=recipe_active_time
        )
        print("Created new_meal:", new_meal)
        session1.add(new_meal)
        session1.commit()
        
        session1.refresh(new_meal)
        new_meal_id = new_meal.meal_id
        print("Obtained new_meal_id:", new_meal_id)
   
    except Exception as x:
        print('First exception:', x)
        return web.json_response({'success': False,
                                  'error_message': 'Вы ввели данные некорректно, проверьте пожалуйста'})
    finally:
        if session1.is_active:
            session1.close()
    print('After 1st block')
    
    session2 = db.Session()
    
    try:
        ids_list = list()
        for i in range(1, (len(data) - 5) // 2 + 1):
            print(i, 'i')
            ingredient_id = data.get(f'ingredient_id{i}')
            ids_list.append(ingredient_id)
        
        if len(set(ids_list)) < len(ids_list):
            raise Exception('Вы выбрали 1 ингредиент несколько раз. Проверьте, пожалуйста')
        del ids_list
        
        list_to_insert_into_gsheets = []
        
        for i in range(1, (len(data) - 5) // 2 + 1):
            print(i, 'i')
            ingredient_id = data.get(f'ingredient_id{i}')
            ingredient_amount = data.get(f'ingredient_amount{i}')
            
            print(ingredient_id, f'ingredient{1}')
            
            ingredient = session2.query(models.Ingredient).filter(
                models.Ingredient.ingredient_id == int(ingredient_id)).first()
            association = models.meal_ingredients_association.insert().values(
                amount=float(ingredient_amount),
                ingredient_id=ingredient.ingredient_id,
                meal_id=int(new_meal_id)
            )
            session2.execute(association)
            list_to_insert_into_gsheets.append([ingredient.ingredient_id, new_meal_id, ingredient_amount])
        
        session2.commit()
        
        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('meals',
                                                                        [[new_meal_id, name, recipe,
                                                                          recipe_active_time, recipe_time,
                                                                          recipe_difficulty]]))
        gsheet_thread.start()
        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('meal_ingredients',
                                                                        list_to_insert_into_gsheets))
        gsheet_thread.start()
        
    except Exception as x:
        session2.rollback()
        meal_to_delete = session2.query(models.Meal).filter(models.Meal.meal_id == new_meal_id).first()
        try:
            session2.delete(meal_to_delete)
            session2.commit()
        except Exception as x:
            print(x)

        if str(x) not in ['Вы выбрали 1 ингредиент несколько раз. Проверьте, пожалуйста']:
            return web.json_response({'success': False,
                                      'error_message': 'Вы ввели данные некорректно, проверьте пожалуйста'})
        else:
            return web.json_response({'success': False,
                                      'error_message': str(x)})
    finally:
        if session2.is_active:
            session2.close()
    
    return web.json_response({'success': True})


@aiohttp_jinja2.template('add_plate.html')
async def add_plate_get(request):
    return {}


async def add_plate_post(request):
    print('Got data')
    data = await request.json()
    tg_id = data.get('tg_id')
    await utils.is_admin_by_id(tg_id)
    
    print(data)
    print('Parsed data')
    
    name = data.get('name')
    plate_type = data.get('plate_type')
    
    session1 = db.Session()
    print('Created session')
    try:
        new_plate = models.Plate(
            plate_name=name,
            plate_type=plate_type
        )
        print("Created new_meal:", new_plate)
        session1.add(new_plate)
        session1.commit()
        
        session1.refresh(new_plate)
        new_plate_id = new_plate.plate_id
        print("Obtain ed new_meal_id:", new_plate_id)
    
    except Exception as x:
        print('First exception:', x)
        return web.json_response({'success': False,
                                  'error_message': 'Вы ввели данные некорректно, проверьте пожалуйста'})
    finally:
        if session1.is_active:
            session1.close()
    print('After 1st block')
    
    session2 = db.Session()
    try:
        percentages_list = list()
        ids_list = list()
        for i in range(1, (len(data) - 2) // 2 + 1):
            print(i, 'i')
            meal_id = data.get(f'meal_id{i}')
            meal_percentage = data.get(f'meal_percentage{i}')
            percentages_list.append(int(meal_percentage))
            ids_list.append(meal_id)
        
        if not 99 <= sum(percentages_list) <= 100:
            raise Exception('Проценты для блюд расставлены некорректно. Проверьте, пожалуйста')
        
        if len(set(ids_list)) < len(ids_list):
            raise Exception('Вы выбрали 1 блюдо несколько раз. Проверьте, пожалуйста')
        
        list_to_insert_into_gsheets = list()
        
        for meal_id, meal_percentage in zip(ids_list, percentages_list):
            meal = session2.query(models.Meal).filter(
                models.Meal.meal_id == int(meal_id)).first()
            association = models.plate_meals_association.insert().values(
                percentage=int(meal_percentage),
                plate_id=int(new_plate_id),
                meal_id=meal.meal_id
            )
            session2.execute(association)
            list_to_insert_into_gsheets.append([new_plate_id, meal.meal_id, meal_percentage])
        
        session2.commit()
        
        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('plates', [[new_plate_id, name, plate_type]]))
        gsheet_thread.start()
        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('plate_meals',
                                                                        list_to_insert_into_gsheets))
        gsheet_thread.start()
    
    except Exception as x:
        session2.rollback()
        plate_to_delete = session2.query(models.Plate).filter(models.Plate.plate_id == new_plate_id).first()
        try:
            session2.delete(plate_to_delete)
            session2.commit()
        except Exception as x:
            print(x)
        
        if str(x) not in ['Проценты для блюд расставлены некорректно. Проверьте, пожалуйста',
                          'Вы выбрали 1 блюдо несколько раз. Проверьте, пожалуйста']:
            return web.json_response({'success': False,
                                      'error_message': 'Вы ввели данные некорректно, проверьте пожалуйста'})
        else:
            return web.json_response({'success': False,
                                      'error_message': str(x)})
    return web.json_response({'success': True})


@aiohttp_jinja2.template('main_view.html')
async def main_view(request):
    return {}


async def get_user_parameters(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    
    session = db.Session()
    try:
        user = session.query(models.User).filter(models.User.tg_id == int(tg_id)).first()
        latest_body_measure = session.query(models.BodyMeasure).filter(models.BodyMeasure.tg_id == int(tg_id)).order_by(models.BodyMeasure.date.desc()).first()
        
        res_data = {
            'weight': latest_body_measure.weight,
            'age': get_age_from_birth_date(datetime.strftime(user.birth_date, "%d.%m.%Y")),
            'height': user.height,
            'weight_aim': user.weight_aim,
            'weight_gap':  float(user.weight_aim) - float(latest_body_measure.weight),
            'plate_diameter': user.plate_diameter
        }
        
        return web.json_response(res_data)
    except Exception as x:
        print(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            session.close()
        

async def get_current_streak(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    
    data = {
        'current_streak': 3,
        'motivational text': 'Так держать! С каждым днём ты получаешь все больше монет и становишься ближе к своей цели!',
        'coins_per_completed_task': 6,
        'coins_loss_for_inactivity': 2,
        'coins_per_completed_task_for_tomorrow': 7
    }
    
    return web.json_response(data)


async def get_nutrient_parameters(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    
    session = db.Session()
    try:
        user = session.query(models.User).filter(models.User.tg_id == tg_id).first()
        
        data = {
            'day_calories': user.day_calories,
            'day_proteins': user.day_proteins,
            'day_fats': user.day_fats,
            'day_carbohydrates': user.day_carbohydrates,
            'eaten_proteins': 10,
            'eaten_fats': 10,
            'eaten_carbohydrates': 190
        }
        
        return web.json_response(data)
    except Exception as x:
        print(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            session.close()


meal_db_func_dict = {
    'mysql': "GROUP_CONCAT(meal_name SEPARATOR ', ')",
    'postgresql': "string_agg(meal_name, ', ')"
}

percentage_db_func_dict = {
    'mysql': "GROUP_CONCAT(CONVERT(percentage, CHAR) SEPARATOR ', ')",
    'postgresql': "string_agg(cast(percentage as text), ', ')"
}

            
async def get_today_plates(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    
    plate_ids = [3, 6, 9]
    
    session = db.Session()
    try:
        plate_ids_as_str = ', '.join([str(x) for x in plate_ids])
        meal_agg_statement = meal_db_func_dict[os.getenv('DB_ENGINE')]
        percentage_agg_statement = percentage_db_func_dict[os.getenv('DB_ENGINE')]
        
        sql_query = text(f"""
        select plate_name, plate_type,
        max(recipe_time) as recipe_time, sum(recipe_active_time) as recipe_active_time,
        max(recipe_difficulty) as recipe_difficulty,
        {percentage_agg_statement} as percentage,
        {meal_agg_statement} as meal_names, sum(calories) as calories, sum(proteins) as proteins,
        sum(fats) as fats, sum(carbohydrates) as carbohydrates
        
        from
        
        (
          select plates.plate_name as plate_name, plate_type, meal_name,
          recipe_time, recipe_active_time, recipe_difficulty, percentage,
          sum(calories*amount) as calories, sum(proteins*amount) as proteins,
          sum(fats*amount) as fats, sum(carbohydrates*amount) as carbohydrates
          
          from
          
          meals inner join meal_ingredients_association using(meal_id)
          inner join ingredients using(ingredient_id)
          inner join plate_meals_association using(meal_id)
          inner join plates using(plate_id)
          where plates.plate_id in ({plate_ids_as_str})
          group by meals.meal_id, meal_name, plate_name, plate_type, recipe_time, recipe_active_time, recipe_difficulty, percentage
        ) as q1
        
        group by plate_name, plate_type;
        """)
        
        # Execute the query
        result = session.execute(sql_query).fetchall()
        print(result)
        result_list = list()

        custom_order = {
            "Завтрак": 1,
            "Обед": 2,
            "Ужин": 3
        }

        # Sort the objects based on the custom order of plate_type
        result.sort(key=lambda obj: custom_order.get(obj.plate_type, float('inf')))
        
        for row in result:
            result_list.append({
                'plate_name': row.plate_name,
                'plate_type': row.plate_type,
                'recipe_time': row.recipe_time,
                'recipe_active_time': row.recipe_active_time,
                'recipe_difficulty': row.recipe_difficulty,
                'meals': row.meal_names.split(', '),
                'percentages': row.percentage.split(', '),
                'calories': row.calories,
                'proteins': row.proteins,
                'fats': row.fats,
                'carbohydrates': row.carbohydrates,
            })
            
        return web.json_response(result_list)
        
    except Exception as x:
        print(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            session.close()


async def get_ingredient_ids_names_properties_list(request):
    session = db.Session()
    try:
        all_ingredients = session.query(models.Ingredient).all()
        data = [{
            'ingredient_id': ingredient.ingredient_id,
            'ingredient_name': ingredient.ingredient_name,
            'measure': ingredient.measure,
            'calories': ingredient.calories,
            'proteins': ingredient.proteins,
            'fats': ingredient.fats,
            'carbohydrates': ingredient.carbohydrates
        }
            for ingredient in all_ingredients]
        
        return web.json_response(data)
    except Exception as x:
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            session.close()


async def get_meal_ids_names_properties_list(request):
    session = db.Session()
    
    sql_query = text(
        "select meals.meal_id as meal_id, meal_name, sum(calories*amount) as calories, "
        "sum(proteins*amount) as proteins, "
        "sum(fats*amount) as fats, sum(carbohydrates*amount) as carbohydrates "
        "from meals "
        "inner join meal_ingredients_association using(meal_id) "
        "inner join ingredients using(ingredient_id) "
        "group by meal_id, meal_name;"
    )
    try:
        # Execute the query
        result = session.execute(sql_query).fetchall()
        result_list = list()
        for row in result:
            result_list.append({
                'meal_id': row.meal_id,
                'meal_name': row.meal_name,
                'calories': row.calories,
                'proteins': row.proteins,
                'fats': row.fats,
                'carbohydrates': row.carbohydrates
            })
        
        return web.json_response(result_list)
    except Exception as x:
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            session.close()


app = web.Application()

app.router.add_static('/static/', path='root/web/static', name='static')

app.add_routes([
    # web.get('/profile/{user_id}', profile_view),
    web.get('/add_ingredient', add_ingredient_get),
    web.get('/add_meal', add_meal_get),
    web.get('/add_plate', add_plate_get),
    web.get('/main', main_view),
    web.get('/api/get_ingredients_list', get_ingredient_ids_names_properties_list),
    web.get('/api/get_meals_list', get_meal_ids_names_properties_list),
])

app.add_routes([
    web.post('/api/is_admin', utils.is_admin_post),
    web.post('/api/add_ingredient', add_ingredient_post),
    web.post('/api/add_meal', add_meal_post),
    web.post('/api/add_plate', add_plate_post),
    
    web.post('/api/get_user_parameters', get_user_parameters),
    web.post('/api/get_current_streak', get_current_streak),
    web.post('/api/get_nutrient_parameters', get_nutrient_parameters),
    web.post('/api/get_today_plates', get_today_plates),
])

aiohttp_jinja2.setup(app, loader=env.loader, context_processors=[aiohttp_jinja2.request_processor])

if __name__ == '__main__':
    # web.run_app(app, host='0.0.0.0')
    web.run_app(app, host='127.0.0.1', port=80)
