import json
import os
import threading

import aiohttp
from aiohttp import web
import jinja2
import aiohttp_jinja2
from sqlalchemy import func, select, text

from root.db import setup as db
from root.db import models
from root.logger.config import logger
from root.tg.main import admin_ids
from root.gsheets import main as gsh
from . import utils

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

        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('meals',
                                                                        [[new_meal_id, name, recipe,
                                                                          recipe_active_time, recipe_time,
                                                                          recipe_difficulty]]))
        gsheet_thread.start()
    
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

        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('plates', [[new_plate_id, name, plate_type]]))
        gsheet_thread.start()
    
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
        for i in range(1, (len(data) - 1) // 2 + 1):
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


async def get_ingredient_ids_names_properties_list(request):
    session = db.Session()
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


async def get_meal_ids_names_properties_list(request):
    session = db.Session()
    
    sql_query = text(
        "select meals.meal_id, meal_name, sum(calories*amount), sum(proteins*amount), "
        "sum(fats*amount), sum(carbohydrates*amount) "
        "from meals "
        "inner join meal_ingredients_association on meals.meal_id = meal_ingredients_association.meal_id "
        "inner join ingredients on ingredients.ingredient_id = meal_ingredients_association.ingredient_id "
        "group by meals.meal_id, meal_name;"
    )
    
    # Execute the query
    result = session.execute(sql_query)
    result_list = []
    for row in result:
        result_list.append({
            'meal_id': row[0],
            'meal_name': row[1],
            'calories': row[2],
            'proteins': row[3],
            'fats': row[4],
            'carbohydrates': row[5]
        })
    
    return web.json_response(result_list)


app = web.Application()

app.router.add_static('/static/', path='root/web/static', name='static')

app.add_routes([
    # web.get('/profile/{user_id}', profile_view),
    web.get('/add_ingredient', add_ingredient_get),
    web.get('/add_meal', add_meal_get),
    web.get('/add_plate', add_plate_get),
    web.get('/api/get_ingredients_list', get_ingredient_ids_names_properties_list),
    web.get('/api/get_meals_list', get_meal_ids_names_properties_list),
])

app.add_routes([
    web.post('/api/is_admin', utils.is_admin_post),
    web.post('/api/add_ingredient', add_ingredient_post),
    web.post('/api/add_meal', add_meal_post),
    web.post('/api/add_plate', add_plate_post),
])

aiohttp_jinja2.setup(app, loader=env.loader, context_processors=[aiohttp_jinja2.request_processor])

if __name__ == '__main__':
    # web.run_app(app, host='0.0.0.0')
    web.run_app(app, host='127.0.0.1', port=80)
