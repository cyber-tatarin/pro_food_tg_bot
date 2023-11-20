import json
import os
import threading
from datetime import datetime, date, timedelta

import aiohttp
from aiohttp import web
import jinja2
import aiohttp_jinja2
from sqlalchemy import func, select, text, desc
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.exc import IntegrityError

from root.db import setup as db
from root.db import models
from root.logger.config import logger
from root.tg.main import admin_ids, get_user_question_type, get_has_eaten_without_plates, what_else_to_eat
from root.tg.utils import get_age_from_birth_date, is_valid_weight, is_valid_birth_date, is_valid_height
from root.gsheets import main as gsh
from . import utils
from root.tg.texts import db_error_message

load_dotenv(find_dotenv())

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join('root', 'web', 'templates')),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True
)

streak_tasks = {
    1: 'Выполни сегодня все задания, чтобы получить награду в ЖИРкоинах, '
       'за которые Вы можете купить косультацию Татьяны. 1 консультация стоит 10 000 ЖИРкоинов. Вы их легко накопите, '
       'если будете заходить 30 дней подряд и выполнять все задания.\n\n'
       'Первое задание — зайти сегодня в приложение — уже выполнено!\n\n'
       'Второе задание — составить рацион на сегодня из 3 приемов пищи. Листайте ниже и нажимайте на кнопку '
       '"Составить рацион на сегодня"',
    2: 'Ура! Второе задание выполнено! Задание №3 — съесть все 3 приема пищи и отметить это в приложении.',
    3: 'Сегодня все задания выполнены. Возвращайтесь завтра!'
}


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
        await session.commit()
        await session.refresh(new_ingredient)
        new_ingredient_id = new_ingredient.ingredient_id
        
        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('ingredients',
                                                                        [[new_ingredient_id, name, measure,
                                                                          calories, proteins,
                                                                          fats, carbohydrates]]))
        gsheet_thread.start()
    
    except Exception as x:
        logger.exception(x)
        return web.json_response({'success': False,
                                  'error_message': 'Вы ввели данные некорректно, проверьте пожалуйста'})
    finally:
        if session.is_active:
            await session.close()
    
    return web.json_response({'success': True})


@aiohttp_jinja2.template('add_meal.html')
async def add_meal_get(request):
    return {}


async def add_meal_post(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    await utils.is_admin_by_id(tg_id)
    
    name = data.get('name')
    recipe = data.get('recipe')
    
    recipe_time = data.get('recipe_time')
    recipe_active_time = data.get('recipe_active_time')
    recipe_difficulty = data.get('recipe_difficulty')
    
    session1 = db.Session()
    try:
        new_meal = models.Meal(
            meal_name=name,
            recipe=recipe,
            recipe_time=recipe_time,
            recipe_difficulty=recipe_difficulty,
            recipe_active_time=recipe_active_time
        )
        session1.add(new_meal)
        await session1.commit()
        
        await session1.refresh(new_meal)
        new_meal_id = new_meal.meal_id
    
    except Exception as x:
        logger.exception(x)
        return web.json_response({'success': False,
                                  'error_message': 'Вы ввели данные некорректно, проверьте пожалуйста'})
    finally:
        if session1.is_active:
            await session1.close()
    
    session2 = db.Session()
    
    try:
        ids_list = list()
        for i in range(1, (len(data) - 5) // 2 + 1):
            ingredient_id = data.get(f'ingredient_id{i}')
            ids_list.append(ingredient_id)
        
        if len(set(ids_list)) < len(ids_list):
            raise Exception('Вы выбрали 1 ингредиент несколько раз. Проверьте, пожалуйста')
        del ids_list
        
        list_to_insert_into_gsheets = []
        
        for i in range(1, (len(data) - 5) // 2 + 1):
            ingredient_id = data.get(f'ingredient_id{i}')
            ingredient_amount = data.get(f'ingredient_amount{i}')
            
            ingredient = await session2.get(models.Ingredient, ingredient_id)
            
            association = models.meal_ingredients_association.insert().values(
                amount=float(ingredient_amount),
                ingredient_id=ingredient.ingredient_id,
                meal_id=int(new_meal_id)
            )
            await session2.execute(association)
            list_to_insert_into_gsheets.append([ingredient.ingredient_id, new_meal_id, ingredient_amount])
        
        await session2.commit()
        
        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('meals',
                                                                        [[new_meal_id, name, recipe,
                                                                          recipe_active_time, recipe_time,
                                                                          recipe_difficulty]]))
        gsheet_thread.start()
        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('meal_ingredients',
                                                                        list_to_insert_into_gsheets))
        gsheet_thread.start()
    
    except Exception as x:
        await session2.rollback()
        meal_to_delete = session2.query(models.Meal).filter(models.Meal.meal_id == new_meal_id).first()
        try:
            await session2.delete(meal_to_delete)
            await session2.commit()
        except Exception as x:
            logger.exception(x)
        
        if str(x) not in ['Вы выбрали 1 ингредиент несколько раз. Проверьте, пожалуйста']:
            return web.json_response({'success': False,
                                      'error_message': 'Вы ввели данные некорректно, проверьте пожалуйста'})
        else:
            return web.json_response({'success': False,
                                      'error_message': str(x)})
    finally:
        if session2.is_active:
            await session2.close()
    
    return web.json_response({'success': True})


@aiohttp_jinja2.template('add_plate.html')
async def add_plate_get(request):
    return {}


async def add_plate_post(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    await utils.is_admin_by_id(tg_id)
    
    name = data.get('name')
    plate_type = data.get('plate_type')
    
    session1 = db.Session()
    try:
        new_plate = models.Plate(
            plate_name=name,
            plate_type=plate_type
        )
        session1.add(new_plate)
        await session1.commit()
        
        await session1.refresh(new_plate)
        new_plate_id = new_plate.plate_id
    
    except Exception as x:
        logger.exception(x)
        return web.json_response({'success': False,
                                  'error_message': 'Вы ввели данные некорректно, проверьте пожалуйста'})
    finally:
        if session1.is_active:
            await session1.close()
    
    session2 = db.Session()
    try:
        percentages_list = list()
        ids_list = list()
        for i in range(1, (len(data) - 2) // 2 + 1):
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
            meal = await session2.get(models.Meal, meal_id)
            association = models.plate_meals_association.insert().values(
                percentage=int(meal_percentage),
                plate_id=int(new_plate_id),
                meal_id=meal.meal_id
            )
            await session2.execute(association)
            list_to_insert_into_gsheets.append([new_plate_id, meal.meal_id, meal_percentage])
        
        await session2.commit()
        
        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('plates', [[new_plate_id, name, plate_type]]))
        gsheet_thread.start()
        gsheet_thread = threading.Thread(target=gsh.add_to_sheet, args=('plate_meals',
                                                                        list_to_insert_into_gsheets))
        gsheet_thread.start()
    
    except Exception as x:
        logger.exception(x)
        await session2.rollback()
        plate_to_delete = await session2.get(models.Plate, new_plate_id)
        try:
            await session2.delete(plate_to_delete)
            await session2.commit()
        except Exception as x:
            logger.exception(x)
        
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
        user = await session.get(models.User, tg_id)
        latest_body_measure_query = await session.execute(select(models.BodyMeasure).where(
            models.BodyMeasure.tg_id == tg_id
        ).order_by(models.BodyMeasure.date.desc()))
        
        latest_body_measure = latest_body_measure_query.scalars().first()
        
        res_data = {
            'weight': latest_body_measure.weight,
            'age': get_age_from_birth_date(datetime.strftime(user.birth_date, "%d.%m.%Y")),
            'height': user.height,
            'weight_aim': user.weight_aim,
            'weight_gap': float(user.weight_aim) - float(latest_body_measure.weight),
            'plate_diameter': user.plate_diameter,
            'gender': user.gender,
            'balance': user.balance
        }
        
        return web.json_response(res_data)
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            await session.close()


async def get_current_streak(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    
    current_task_number = 1
    session = db.Session()
    today = date.today()
    try:
        user_streak_obj = await session.get(models.UserStreak, tg_id)
        if user_streak_obj is None:
            user_streak_obj = models.UserStreak(tg_id=tg_id, streak=0)
            session.add(user_streak_obj)
            await session.commit()
            await session.refresh(user_streak_obj)
        
        current_streak = user_streak_obj.streak
        if user_streak_obj.last_updated != today:
            
            all_today_chosen_plates_query = await session.execute(select(models.UserPlatesDate).where(
                models.UserPlatesDate.tg_id == tg_id,
                models.UserPlatesDate.date == today)
            )
            all_today_chosen_plates = all_today_chosen_plates_query.scalars().all()
            
            if all_today_chosen_plates:
                if len(all_today_chosen_plates) >= 3:
                    current_task_number += 1
            
            # all_today_has_eaten = session.query(models.HasEaten).filter(models.HasEaten.tg_id == tg_id,
            #                                                             models.HasEaten.date == today).all()
            # if all_today_has_eaten:
            #     if len(all_today_has_eaten) >= 3:
            #         current_task_number += 1
            
            # if current_task_number == 3:
            #     pass
        else:
            current_task_number = 3
    
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()
    
    finally:
        if session.is_active:
            await session.close()
    
    day_word = await utils.get_day_word_according_to_number(current_streak)
    coin_reward_base = 23 + 23 * current_streak if current_task_number < 3 else 23 + 23 * (current_streak-1)
    coin_reward_word = await utils.get_coin_word_according_to_number(coin_reward_base)
    
    tommorow_coin_reward = coin_reward_base + 23
    tomorrow_coin_word = await utils.get_coin_word_according_to_number(tommorow_coin_reward)
    
    data = {
        'current_streak_text': f'{current_streak} {day_word} подряд',
        'current_task_number': current_task_number,
        'coin_reward': f'{coin_reward_base} {coin_reward_word}',
        'task_text': streak_tasks[current_task_number],
        'tomorrow_text': f'Завтра Вы получите {tommorow_coin_reward} {tomorrow_coin_word}',
    }
    
    return web.json_response(data)


async def get_nutrient_parameters(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    
    session = db.Session()
    try:
        today = date.today()
        user = await session.get(models.User, tg_id)
        
        stmt = (
            select(
                func.coalesce(func.sum(models.HasEaten.calories), 0),
                func.coalesce(func.sum(models.HasEaten.proteins), 0),
                func.coalesce(func.sum(models.HasEaten.fats), 0),
                func.coalesce(func.sum(models.HasEaten.carbohydrates), 0)
            )
            .where(
                models.HasEaten.date_time >= today,
                models.HasEaten.date_time < today + timedelta(days=1),
                models.HasEaten.tg_id == tg_id
            )
        )
        
        # Fetching the results asynchronously
        result = await session.execute(stmt)
        sums = result.fetchone()
        
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
        logger.exception(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            await session.close()


async def get_today_plates(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    
    session1 = db.Session()
    try:
        today = date.today()
        today_plates_list_query = await session1.execute(select(models.UserPlatesDate).where
                                                         (models.UserPlatesDate.tg_id == tg_id,
                                                          models.UserPlatesDate.date == today,
                                                          ))
        today_plates_list = today_plates_list_query.scalars().all()
    
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()
    finally:
        if session1.is_active:
            await session1.close()
    
    if today_plates_list:
        plate_ids = [int(element.plate_id) for element in today_plates_list]
        
        session2 = db.Session()
        try:
            result_list = await utils.get_nutrient_for_plates_by_ids(session2, tg_id, plate_ids, in_json=True)
            all_today_has_eaten_plates_query = await session2.execute(select(models.HasEaten).where(
                models.HasEaten.date_time >= today,
                models.HasEaten.date_time < today + timedelta(days=1),
                models.HasEaten.tg_id == tg_id
            ))
            all_today_has_eaten_plates = all_today_has_eaten_plates_query.scalars().all()
            
            all_favorites_query = await session2.execute(
                select(models.Favorites).where(models.Favorites.tg_id == tg_id))
            all_favorites = all_favorites_query.scalars().all()
            
            await utils.set_plate_type(result_list, today_plates_list)
            await utils.restore_duplicate_plate_if_exists(result_list, plate_ids)
            await utils.set_is_eaten_true_for_plates_in_result_list(result_list, all_today_has_eaten_plates)
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
            logger.exception(x)
            return web.HTTPBadGateway()
        finally:
            if session2.is_active:
                await session2.close()
    
    else:
        return web.json_response([])


async def get_ingredient_ids_names_properties_list(request):
    session = db.Session()
    try:
        all_ingredients_query = await session.execute(select(models.Ingredient))
        all_ingredients = all_ingredients_query.scalars().all()
        
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
            await session.close()


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
        result_query = await session.execute(sql_query)
        result = result_query.fetchall()
        
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
        logger.exception(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            await session.close()


async def get_all_plates_to_choose(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    plate_type = data.get('plate_type')
    
    session = db.Session()
    try:
        today = date.today()
        chosen_plate_query = await session.execute(
            select(models.UserPlatesDate).where(models.UserPlatesDate.tg_id == tg_id,
                                                models.UserPlatesDate.plate_type == plate_type,
                                                models.UserPlatesDate.date == today))
        chosen_plate = chosen_plate_query.scalar_one_or_none()
        
        all_favorites_query = await session.execute(select(models.Favorites).filter(models.Favorites.tg_id == tg_id))
        all_favorites = all_favorites_query.scalars().all()

        result_list = await utils.get_nutrient_for_plates_by_ids(session, tg_id, in_json=True)
        await utils.set_in_favorites_true_for_plates_in_result_list(result_list, all_favorites)
        await utils.put_chosen_plate_to_0_index_if_exists(result_list, chosen_plate)
        
        if len(result_list) > 4:
            return web.json_response({
                'chosen_plate': result_list[0],
                'recommended_plates': result_list[1:4],
                'all_plates': result_list[4:]
            })
        else:
            return web.HTTPBadGateway()
    
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            await session.close()


async def has_eaten_plate(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    plate_id = data.get('plate_id')
    plate_type = data.get('plate_type')
    
    calories = data.get('calories')
    proteins = data.get('proteins')
    fats = data.get('fats')
    carbohydrates = data.get('carbohydrates')
    
    current_balance = ''
    
    session = db.Session()
    try:
        today = date.today()
        eaten_plate_query = await session.execute(select(models.HasEaten).where(
            models.HasEaten.date == today,
            models.HasEaten.tg_id == tg_id,
            models.HasEaten.plate_type == plate_type
        ))
        eaten_plate = eaten_plate_query.scalar_one_or_none()
        
        user_streak_obj = await session.get(models.UserStreak, tg_id)
        
        if eaten_plate is None:
            new_has_eaten = models.HasEaten(tg_id=tg_id, plate_id=plate_id,
                                            calories=calories, proteins=proteins,
                                            fats=fats, carbohydrates=carbohydrates, plate_type=plate_type)
            session.add(new_has_eaten)
            await session.commit()
            completed_all_tasks = False
            today_reward = 23
            try:
                all_today_has_eaten_query = await session.execute(
                    select(models.HasEaten).where(models.HasEaten.tg_id == tg_id,
                                                  models.HasEaten.date == today))
                all_today_has_eaten = all_today_has_eaten_query.scalars().all()
                
                if all_today_has_eaten:
                    if len(all_today_has_eaten) >= 3:
                        
                        updated_earlier_than_today_or_created_today = True
                        await session.refresh(user_streak_obj)
                        last_updated = user_streak_obj.last_updated
                        if last_updated is not None:
                            updated_earlier_than_today_or_created_today = user_streak_obj.last_updated < today
                        
                        if updated_earlier_than_today_or_created_today:
                            
                            user_obj = await session.get(models.User, tg_id)
                            today_reward = 23 + float(user_streak_obj.streak) * 23
                            user_obj.balance += today_reward
                            
                            user_streak_obj.streak += 1
                            
                            current_balance = user_obj.balance
                            
                            await session.commit()
                            completed_all_tasks = True
            
            except Exception as x:
                logger.exception(x)
            
            response_dict = {'success': True, 'is_green': False, 'completed_all_tasks': completed_all_tasks}
            if completed_all_tasks:
                reward_word = await utils.get_coin_word_according_to_number(today_reward)
                response_dict['bold_text'] = f'Так держать Вы получили {today_reward} {reward_word}'
                coin_word = await utils.get_coin_word_according_to_number(current_balance)
                response_dict['thin_text'] = f'Теперь у Вас на балансе {current_balance} {coin_word}'
            
            return web.json_response(response_dict)
        
        else:
            await session.delete(eaten_plate)
            await session.commit()
            
            return web.json_response({'success': True, 'is_green': True, 'completed_all_tasks': False})
    
    except Exception as x:
        logger.exception(x)
        return web.json_response({'success': False})
    
    finally:
        if session.is_active:
            await session.close()


async def add_to_favorites(request):
    data = await request.json()
    
    plate_id = data.get('plate_id')
    tg_id = data.get('tg_id')
    
    session = db.Session()
    try:
        new_favorite = models.Favorites(tg_id=tg_id, plate_id=plate_id)
        session.add(new_favorite)
        await session.commit()
        
        return web.json_response({'success': True, 'is_black': False})
    
    except Exception as x:
        try:
            session.rollback()
            favorite_to_delete_query = await session.execute(
                select(models.Favorites).where(models.Favorites.tg_id == tg_id,
                                                models.Favorites.plate_id == plate_id))
            favorite_to_delete = favorite_to_delete_query.scalar_one_or_none()
            await session.delete(favorite_to_delete)
            await session.commit()
            
            return web.json_response({'success': True, 'is_black': True})
        
        except Exception as x:
            logger.exception(x)
            return web.json_response({'success': False})
    
    finally:
        if session.is_active:
            await session.close()


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


# async def get_all_favorites(request):
#     data = await request.json()
#
#     tg_id = data.get('tg_id')
#
#     session = db.Session()
#     try:
#         all_favorites = session.query(models.Favorites).filter(models.Favorites.tg_id == tg_id).all()
#         return web.json_response({'success': True})
#
#     except Exception as x:
#         print(x)
#         return web.json_response({'success': False})


@aiohttp_jinja2.template('choose_breakfast.html')
async def choose_breakfast(request):
    return {}


@aiohttp_jinja2.template('choose_lunch.html')
async def choose_lunch(request):
    return {}


@aiohttp_jinja2.template('choose_dinner.html')
async def choose_dinner(request):
    return {}


@aiohttp_jinja2.template('favorites.html')
async def favorites(request):
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
        await session.commit()
    
    except IntegrityError:
        new_session = db.Session()
        try:
            obj_to_edit_query = await new_session.execute(select(models.UserPlatesDate).where(
                models.UserPlatesDate.tg_id == tg_id,
                models.UserPlatesDate.plate_type == plate_type,
                models.UserPlatesDate.date == date.today()))
            obj_to_edit = obj_to_edit_query.scalar_one_or_none()
            
            obj_to_edit.plate_id = plate_id
            await new_session.commit()
        except Exception as x:
            logger.exception(x)
            return web.HTTPBadGateway()
        finally:
            if session.is_active:
                await session.close()
        return web.json_response({'success': True})
    
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            await session.close()
    
    return web.json_response({'success': True})


async def get_all_favorites(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    plate_type = data.get('plate_type')
    
    session = db.Session()
    try:
        today = date.today()
        chosen_plate_query = await session.execute(select(models.UserPlatesDate).where(models.UserPlatesDate.tg_id == tg_id,
                                                                   models.UserPlatesDate.plate_type == plate_type,
                                                                   models.UserPlatesDate.date == today))
        chosen_plate = chosen_plate_query.scalar_one_or_none()
        
        all_favorites_query = await session.execute(select(models.Favorites).filter(models.Favorites.tg_id == tg_id))
        all_favorites = all_favorites_query.scalars().all()
        favorites_plate_ids = [int(element.plate_id) for element in all_favorites]

        result_list = await utils.get_nutrient_for_plates_by_ids(session, tg_id, in_json=True, plate_ids=favorites_plate_ids)
        await utils.set_in_favorites_true_for_plates_in_result_list(result_list, all_favorites)
        
        if chosen_plate is not None:
            if chosen_plate.plate_id not in favorites_plate_ids:
                chosen_plate = None
        await utils.put_chosen_plate_to_0_index_if_exists(result_list, chosen_plate)
        
        if len(result_list) > 1:
            return web.json_response({
                'chosen_plate': result_list[0],
                'all_plates': result_list[1:]
            })
        else:
            return web.json_response({
                'chosen_plate': result_list[0],
                'all_plates': []
            })
    
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            await session.close()


async def get_recipe(request):
    data = await request.json()
    
    plate_id = data.get('plate_id')
    tg_id = data.get('tg_id')
    
    session = db.Session()
    try:
        result_dict = await utils.get_recipe_values(session, plate_id, tg_id)
        if result_dict:
            return web.json_response(result_dict)
        else:
            return web.HTTPBadGateway()
    
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()
    
    finally:
        if session.is_active:
            await session.close()


async def ask_question(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    
    try:
        await get_user_question_type(tg_id)
        return web.json_response({'success': True})
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()


async def submit_plate_review(request):
    data = await request.json()
    
    tg_id = data.get('tg_id')
    plate_id = data.get('plate_id')
    mark = data.get('mark')
    
    session = db.Session()
    try:
        new_plate_review = models.PlateReview(tg_id=tg_id,
                                              plate_id=plate_id,
                                              mark=mark)
        
        session.add(new_plate_review)
        await session.commit()
        return web.json_response({'success': True})
    
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            await session.close()


async def get_has_eaten_without_plates_post(request):
    data = await request.json()
    try:
        tg_id = data['tg_id']
        await get_has_eaten_without_plates(tg_id)
        return web.json_response({'success': True})
    
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()


async def what_else_to_eat_post(request):
    data = await request.json()
    try:
        tg_id = data['tg_id']
        await what_else_to_eat(tg_id)
        return web.json_response({'success': True})
    
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()


@aiohttp_jinja2.template('statistics.html')
async def statistics_get(request):
    return {}


async def statistics_post(request):
    data = await request.json()
    tg_id = data.get('tg_id')
    
    session = db.Session()
    try:
        all_body_measures_query = await session.execute(select(models.BodyMeasure).where
        (models.BodyMeasure.tg_id == tg_id).order_by(
            models.BodyMeasure.date)
        )
        
        all_body_measures = all_body_measures_query.scalars().all()
        all_body_measures.pop(0)
        
        if all_body_measures:
            weight_list = list()
            chest_volume_list = list()
            underchest_volume_list = list()
            waist_volume_list = list()
            belly_volume_list = list()
            hips_volume_list = list()
            
            date_pattern = '%d.%m.%Y'
            
            for index, body_measure_obj in enumerate(all_body_measures[1:]):
                previous_body_measure_obj = all_body_measures[index]
                
                obj_date_as_str = datetime.strftime(previous_body_measure_obj.date, date_pattern)
                
                weight_list.append({'date': obj_date_as_str, 'value': previous_body_measure_obj.weight})
                chest_volume_list.append({'date': obj_date_as_str, 'value': previous_body_measure_obj.chest_volume})
                underchest_volume_list.append(
                    {'date': obj_date_as_str, 'value': previous_body_measure_obj.underchest_volume})
                waist_volume_list.append({'date': obj_date_as_str, 'value': previous_body_measure_obj.waist_volume})
                belly_volume_list.append({'date': obj_date_as_str, 'value': previous_body_measure_obj.belly_volume})
                hips_volume_list.append({'date': obj_date_as_str, 'value': previous_body_measure_obj.hips_volume})
                
                measure_date = previous_body_measure_obj.date
                while (body_measure_obj.date - measure_date).days > 7:
                    measure_date = measure_date + timedelta(days=7)
                    measure_date_as_str = datetime.strftime(measure_date, date_pattern)
                    
                    weight_list.append({'date': measure_date_as_str, 'value': None})
                    chest_volume_list.append({'date': measure_date_as_str, 'value': None})
                    underchest_volume_list.append({'date': measure_date_as_str, 'value': None})
                    waist_volume_list.append({'date': measure_date_as_str, 'value': None})
                    belly_volume_list.append({'date': measure_date_as_str, 'value': None})
                    hips_volume_list.append({'date': measure_date_as_str, 'value': None})
            
            last_obj_date = datetime.strftime(all_body_measures[-1].date, date_pattern)
            
            weight_list.append({'date': last_obj_date, 'value': all_body_measures[-1].weight})
            chest_volume_list.append({'date': last_obj_date, 'value': all_body_measures[-1].chest_volume})
            underchest_volume_list.append({'date': last_obj_date, 'value': all_body_measures[-1].underchest_volume})
            waist_volume_list.append({'date': last_obj_date, 'value': all_body_measures[-1].waist_volume})
            belly_volume_list.append({'date': last_obj_date, 'value': all_body_measures[-1].belly_volume})
            hips_volume_list.append({'date': last_obj_date, 'value': all_body_measures[-1].hips_volume})
            
            result_dict = {
                'weight_list': weight_list,
                'chest_volume_list': chest_volume_list,
                'underchest_volume_list': underchest_volume_list,
                'waist_volume_list': waist_volume_list,
                'belly_volume_list': belly_volume_list,
                'hips_volume_list': hips_volume_list
            }
            
            return web.json_response(result_dict)
    
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            await session.close()
            

@aiohttp_jinja2.template('update_profile.html')
async def update_profile_get(request):
    return {}


@aiohttp_jinja2.template('update_weight_aim.html')
async def update_weight_aim_get(request):
    return {}


async def update_weight_aim_post(request):
    data = await request.json()
    weight_aim = data.get('weight_aim')
    tg_id = data.get('tg_id')
    session = db.Session()
    try:
        user = await session.get(models.User, tg_id)
        if is_valid_weight(str(weight_aim)):
            user.weight_aim = weight_aim
            await session.commit()
            return web.json_response({'success': True})
        else:
            return web.json_response({'success': False, 'error_message': 'Цель по весу введена некорректно. '
                                                                         'Проверьте, чтобы это было целое число '
                                                                         'либо число в формате 80.4'})
    except Exception as x:
        logger.exception(x)
        return web.json_response({'success': False, 'error_message': db_error_message})
    finally:
        await session.close()
        

async def update_profile_post(request):
    data = await request.json()
    height = data.get('height')
    birth_date = data.get('date')
    
    tg_id = data.get('tg_id')
    session = db.Session()
    try:
        if is_valid_height(str(height)):
            birth_date_strp = datetime.strptime(birth_date, '%d-%m-%Y')
            birth_date = datetime.strftime(birth_date_strp, '%d.%m.%Y')
            if is_valid_birth_date(str(birth_date)):
                user = await session.get(models.User, tg_id)
                user.height = height
                user.birth_date = birth_date_strp
                await session.commit()
                return web.json_response({'success': True})
            else:
                return web.json_response({'success': False, 'error_message': 'Дата рождения введена некорректно. '
                                                                             'Проверьте, чтобы формат соответствовал '
                                                                             '"31.12.1999"'})
        else:
            return web.json_response({'success': False, 'error_message': 'Рост введён некорректно. '
                                                                         'Проверьте, чтобы это было целое число'})
    except Exception as x:
        logger.exception(x)
        return web.json_response({'success': False, 'error_message': db_error_message})
    finally:
        await session.close()
        

async def get_data_for_profile_update_post(request):
    data = await request.json()
    
    tg_id = data.get('tg_id')
    session = db.Session()
    try:
        user = await session.get(models.User, tg_id)
        return web.json_response({'height': user.height, 'birth_date': user.birth_date})
    except Exception as x:
        logger.exception(x)
        return web.HTTPBadGateway()
    finally:
        if session.is_active:
            session.close()


async def get_data_for_weight_aim_update_post(request):
    data = await request.json()
    
    tg_id = data.get('tg_id')
    session = db.Session()
    try:
        user = await session.get(models.User, tg_id)
        return web.json_response({'weight_aim': user.weight_aim})
    except Exception as x:
        logger.exception(x)
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
    web.get('/choose_breakfast', choose_breakfast),
    web.get('/choose_lunch', choose_lunch),
    web.get('/choose_dinner', choose_dinner),
    web.get('/favorites', favorites),
    web.get('/statistics', statistics_get),
    web.get('/update_profile', update_profile_get),
    web.get('/update_weight_aim', update_weight_aim_get)

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
    web.post('/api/get_all_favorites', get_all_favorites),
    web.post('/api/get_recipe', get_recipe),
    web.post('/api/ask_question', ask_question),
    web.post('/api/submit_plate_review', submit_plate_review),
    web.post('/api/get_has_eaten_without_plates_post', get_has_eaten_without_plates_post),
    web.post('/api/what_else_to_eat_post', what_else_to_eat_post),
    web.post('/api/statistics', statistics_post),
    web.post('/api/update_profile_post', update_profile_post),
    web.post('/api/update_weight_aim_post', update_weight_aim_post),
    web.post('/api/get_data_for_profile_update_post', get_data_for_profile_update_post),
    web.post('/api/get_data_for_weight_aim_update_post', get_data_for_weight_aim_update_post),
    # web.post('/api/remove_from_favorites', remove_from_favorites),

])

aiohttp_jinja2.setup(app, loader=env.loader, context_processors=[aiohttp_jinja2.request_processor])

if __name__ == '__main__':
    # web.run_app(app, host='0.0.0.0')
    web.run_app(app, host='127.0.0.1', port=80)
