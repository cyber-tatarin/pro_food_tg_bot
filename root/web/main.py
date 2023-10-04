import json
import os
import threading
from datetime import datetime, date, timedelta

import aiohttp
from aiohttp import web
import jinja2
import aiohttp_jinja2
from sqlalchemy import func, select, text
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.exc import IntegrityError

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
    
    # session3 = db.Session()
    # try:
    #     result = await utils.get_nutrient_for_plates_by_ids(session3, [new_plate_id])
    #     plate_obj = session3.query(models.Plate).filter(models.Plate.plate_id == new_plate_id).first()
    #
    #     plate_obj.calories = result[0].calories
    #     plate_obj.proteins = result[0].proteins
    #     plate_obj.fats = result[0].fats
    #     plate_obj.carbohydrates = result[0].carbohydrates
    #
    #     session3.commit()
    #
    # except Exception as x:
    #     print(x)
    #     return web.json_response({'success': False,
    #                               'error_message': 'Блюда сохранены, но произошла ошибка при высчитывании информации '
    #                                                'о питательных веществах. Пожалуйста, свяжитесь с разработчиком'})
    
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
        latest_body_measure = session.query(models.BodyMeasure).filter(
            models.BodyMeasure.tg_id == int(tg_id)
        ).order_by(models.BodyMeasure.date.desc()).first()
        
        res_data = {
            'weight': latest_body_measure.weight,
            'age': get_age_from_birth_date(datetime.strftime(user.birth_date, "%d.%m.%Y")),
            'height': user.height,
            'weight_aim': user.weight_aim,
            'weight_gap': float(user.weight_aim) - float(latest_body_measure.weight),
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
        'motivational_text': 'Так держать! С каждым днём ты получаешь все больше монет и становишься ближе к своей цели!',
        'tasks': [
            {
                'text': 'Составить рацион',
                'completed': True
            },
            {
                'text': 'Съесть рацион',
                'completed': False
            }
        ],
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
        today = date.today()
        user = session.query(models.User).filter(models.User.tg_id == tg_id).first()
        all_today_has_eaten_query = session.query(
            func.coalesce(func.sum(models.HasEaten.calories), 0),
            func.coalesce(func.sum(models.HasEaten.proteins), 0),
            func.coalesce(func.sum(models.HasEaten.fats), 0),
            func.coalesce(func.sum(models.HasEaten.carbohydrates), 0)
        ).filter(
            models.HasEaten.date_time >= today,
            models.HasEaten.date_time < today + timedelta(days=1),
            models.HasEaten.tg_id == tg_id
        )
        
        # Fetch the results (returns a tuple with sum values)
        sums = all_today_has_eaten_query.one()
        
        sum_calories, sum_proteins, sum_fats, sum_carbohydrates = sums
        
        data = {
            'day_calories': user.day_calories,
            'day_proteins': user.day_proteins,
            'day_fats': user.day_fats,
            'day_carbohydrates': user.day_carbohydrates,
            'eaten_calories': int(sum_calories),
            'eaten_proteins': int(sum_proteins),
            'eaten_fats': int(sum_fats),
            'eaten_carbohydrates': int(sum_carbohydrates)
        }
        
        return web.json_response(data)
    except Exception as x:
        print(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            session.close()


async def get_today_plates(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    
    session1 = db.Session()
    try:
        today = date.today()
        today_plates_list = session1.query(models.UserPlatesDate).filter(models.UserPlatesDate.tg_id == tg_id,
                                                                         models.UserPlatesDate.date == today,
                                                                         ).all()
    
    except Exception as x:
        print(x)
        return web.HTTPBadGateway()
    finally:
        if session1.is_active:
            session1.close()
    
    if today_plates_list:
        plate_ids = [int(element.plate_id) for element in today_plates_list]
        
        session2 = db.Session()
        try:
            result_list = await utils.get_nutrient_for_plates_by_ids(session2, plate_ids, in_json=True)
            all_today_has_eaten_plates = session2.query(models.HasEaten).filter(
                models.HasEaten.date_time >= today,
                models.HasEaten.date_time < today + timedelta(days=1),
                models.HasEaten.tg_id == tg_id
            ).all()
            
            all_favorites = session2.query(models.Favorites).filter(models.Favorites.tg_id == tg_id).all()
            
            await utils.set_is_eaten_true_for_plates_in_result_list(result_list, all_today_has_eaten_plates)
            await utils.set_plate_type(result_list, today_plates_list)
            await utils.set_in_favorites_true_for_plates_in_result_list(result_list, all_favorites)
            
            custom_order = {
                "Завтрак": 1,
                "Обед": 2,
                "Ужин": 3
            }
            
            # # Sort the objects based on the custom order of plate_type
            result_list.sort(key=lambda obj: custom_order.get(obj['plate_type'], float('inf')))
            
            return web.json_response(result_list)
            # return web.json_response([])
        
        except Exception as x:
            print(x)
            return web.HTTPBadGateway()
        finally:
            if session2.is_active:
                session2.close()
    
    else:
        return web.json_response([])


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


async def get_all_plates_to_choose(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    plate_type = data.get('plate_type')
    
    session = db.Session()
    try:
        print('before db')
        today = date.today()
        chosen_plate = session.query(models.UserPlatesDate).filter(models.UserPlatesDate.tg_id == tg_id,
                                                                   models.UserPlatesDate.plate_type == plate_type,
                                                                   models.UserPlatesDate.date == today).first()
        
        all_favorites = session.query(models.Favorites).filter(models.Favorites.tg_id == tg_id).all()
        
        print('inside')
        result_list = await utils.get_nutrient_for_plates_by_ids(session, in_json=True)
        await utils.put_chosen_plate_to_0_index_if_exists(result_list, chosen_plate)
        await utils.set_in_favorites_true_for_plates_in_result_list(result_list, all_favorites)
        
        if len(result_list) > 4:
            return web.json_response({
                'chosen_plate': result_list[0],
                'recommended_plates': result_list[1:4],
                'all_plates': result_list[4:]
            })
        else:
            return web.HTTPBadGateway()
    
    except Exception as x:
        print(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            session.close()


async def has_eaten_plate(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    plate_id = data.get('plate_id')
    
    calories = data.get('calories')
    proteins = data.get('proteins')
    fats = data.get('fats')
    carbohydrates = data.get('carbohydrates')
    
    session = db.Session()
    try:
        today = date.today()
        all_today_has_eaten_plates = session.query(models.HasEaten).filter(
            models.HasEaten.date_time >= today,
            models.HasEaten.date_time < today + timedelta(days=1),
            models.HasEaten.tg_id == tg_id
        ).all()
        
        eaten_plate_ids = [int(element.plate_id) for element in all_today_has_eaten_plates if
                           element.plate_id is not None]
        
        if int(plate_id) not in eaten_plate_ids:
            new_has_eaten = models.HasEaten(tg_id=tg_id, plate_id=plate_id,
                                            calories=calories, proteins=proteins,
                                            fats=fats, carbohydrates=carbohydrates)
            session.add(new_has_eaten)
            session.commit()
            
            return web.json_response({'success': True, 'is_green': False})
        
        else:
            session.rollback()
            for eaten_plate in all_today_has_eaten_plates:
                session.refresh(eaten_plate)
                if eaten_plate.plate_id == plate_id:
                    session.delete(eaten_plate)
                    session.commit()
                    break
            
            return web.json_response({'success': True, 'is_green': True})
    
    except Exception as x:
        print(x)
        return web.json_response({'success': False})
    
    finally:
        if session.is_active:
            session.close()


async def add_to_favorites(request):
    data = await request.json()
    
    plate_id = data.get('plate_id')
    tg_id = data.get('tg_id')
    
    session = db.Session()
    try:
        new_favorite = models.Favorites(tg_id=tg_id, plate_id=plate_id)
        session.add(new_favorite)
        session.commit()
        
        return web.json_response({'success': True, 'is_black': False})
    
    except Exception as x:
        try:
            session.rollback()
            favorite_to_delete = session.query(models.Favorites).filter(models.Favorites.tg_id == tg_id,
                                                                        models.Favorites.plate_id == plate_id).first()
            session.delete(favorite_to_delete)
            session.commit()

            return web.json_response({'success': True, 'is_black': True})
            
        except Exception as x:
            print(x)
            return web.json_response({'success': False})


# async def remove_from_favorites(request):
#     data = await request.json()
#
#     plate_id = data.get('plate_id')
#     tg_id = data.get('tg_id')
#
#     session = db.Session()
#     try:
#         favorite_to_delete = session.query(models.Favorites).filter(models.Favorites.tg_id == tg_id,
#                                                                     models.Favorites.plate_id == plate_id).first()
#         session.delete(favorite_to_delete)
#         session.commit()
#
#         return web.json_response({'success': True})
#
#     except Exception as x:
#         print(x)
#         return web.json_response({'success': False})


async def get_all_favorites(request):
    data = await request.json()
    
    tg_id = data.get('tg_id')
    
    session = db.Session()
    try:
        all_favorites = session.query(models.Favorites).filter(models.Favorites.tg_id == tg_id).all()
        return web.json_response({'success': True})
    
    except Exception as x:
        print(x)
        return web.json_response({'success': False})


@aiohttp_jinja2.template('choose_breakfast.html')
async def choose_breakfast(request):
    return {}


@aiohttp_jinja2.template('choose_lunch.html')
async def choose_lunch(request):
    return {}


@aiohttp_jinja2.template('choose_dinner.html')
async def choose_dinner(request):
    return {}


async def has_chosen_plate(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    plate_type = data.get('plate_type')
    plate_id = data.get('plate_id')
    
    session = db.Session()
    try:
        new_user_plate_date = models.UserPlatesDate(tg_id=tg_id, plate_type=plate_type, plate_id=plate_id)
        session.add(new_user_plate_date)
        session.commit()
    
    except IntegrityError:
        new_session = db.Session()
        try:
            obj_to_edit = new_session.query(models.UserPlatesDate).filter(models.UserPlatesDate.tg_id == tg_id,
                                                                          models.UserPlatesDate.plate_type == plate_type,
                                                                          models.UserPlatesDate.date == date.today()).first()
            obj_to_edit.plate_id = plate_id
            new_session.commit()
        except Exception as x:
            print(x)
            return web.HTTPBadGateway()
        finally:
            if session.is_active:
                session.close()
        return web.json_response({'success': True})
    
    except Exception as x:
        print(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            session.close()
    
    return web.json_response({'success': True})


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
    web.get('/choose_breakfast', choose_breakfast),
    web.get('/choose_lunch', choose_lunch),
    web.get('/choose_dinner', choose_dinner),

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
    web.post('/api/has_eaten_plate', has_eaten_plate),
    web.post('/api/get_all_plates_to_choose', get_all_plates_to_choose),
    web.post('/api/has_chosen_plate', has_chosen_plate),
    web.post('/api/add_to_favorites', add_to_favorites),
    # web.post('/api/remove_from_favorites', remove_from_favorites),

])

aiohttp_jinja2.setup(app, loader=env.loader, context_processors=[aiohttp_jinja2.request_processor])

if __name__ == '__main__':
    # web.run_app(app, host='0.0.0.0')
    web.run_app(app, host='127.0.0.1', port=80)
