import os
from datetime import datetime

from aiohttp import web
from sqlalchemy import text

from root.db import models
from root.logger.config import logger

from root.tg.main import admin_ids

multiplier_by_plate_diameter = {
    21: 1,
    23: 1.2,
    25: 1.4
}


async def is_admin_post(request):
    json_data = request.json()
    tg_id = json_data.get('tg_id')
    if tg_id in admin_ids:
        return web.json_response({'is_admin': 'true'})
    else:
        return web.json_response({'is_admin': 'false'})


async def is_admin_by_id(tg_id):
    try:
        if int(tg_id) not in admin_ids:
            raise web.HTTPForbidden()
    except Exception as x:
        logger.exception(x)
        raise web.HTTPForbidden()


meal_db_func_dict = {
    'mysql': "GROUP_CONCAT(meal_name SEPARATOR ', ')",
    'postgresql': "string_agg(meal_name, ', ')"
}

percentage_db_func_dict = {
    'mysql': "GROUP_CONCAT(CONVERT(percentage, CHAR) SEPARATOR ', ')",
    'postgresql': "string_agg(cast(percentage as text), ', ')"
}


async def get_nutrient_for_plates_by_ids(session, tg_id, plate_ids=None, in_json=False) -> list:
    if plate_ids is not None:
        if len(plate_ids) == 0:
            return []
        
    meal_agg_statement = meal_db_func_dict[os.getenv('DB_ENGINE')]
    percentage_agg_statement = percentage_db_func_dict[os.getenv('DB_ENGINE')]
    
    sql_query = text(f"""
    select plate_name, plate_type, plate_id,
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
      sum(fats*amount) as fats, sum(carbohydrates*amount) as carbohydrates,
      plates.plate_id as plate_id

      from

      meals inner join meal_ingredients_association using(meal_id)
      inner join ingredients using(ingredient_id)
      inner join plate_meals_association using(meal_id)
      inner join plates using(plate_id)
      {'where plates.plate_id in (' + ', '.join([str(x) for x in plate_ids]) + ')' if plate_ids else ''}
      group by meals.meal_id, plates.plate_id, meal_name, plate_name, plate_type, recipe_time, recipe_active_time,
      recipe_difficulty, percentage
      order by percentage
    ) as q1

    group by plate_name, plate_type, plate_id;
    """)
    
    # Execute the query
    result_query = await session.execute(sql_query)
    result = result_query.fetchall()

    user = await session.get(models.User, tg_id)
    multiplier = multiplier_by_plate_diameter[user.plate_diameter]
    
    print(result)
    
    if not in_json:
        return result
    
    else:
        result_list = list()
        if result:
            for row in result:
                result_list.append({
                    'plate_id': row.plate_id,
                    'plate_name': row.plate_name,
                    'recipe_time': int(row.recipe_time),
                    'recipe_active_time': int(row.recipe_active_time),
                    'recipe_difficulty': int(row.recipe_difficulty),
                    'meals': row.meal_names.split(', '),
                    'percentages': row.percentage.split(', '),
                    'calories': int(row.calories) * multiplier,
                    'proteins': int(row.proteins) * multiplier,
                    'fats': int(row.fats) * multiplier,
                    'carbohydrates': int(row.carbohydrates) * multiplier,
                    'in_favorites': False
                })
        
        return result_list


async def set_is_eaten_true_for_plates_in_result_list(result_list, all_today_has_eaten_plates_query):
    if all_today_has_eaten_plates_query:
        eaten_plate_types = [element.plate_type for element in all_today_has_eaten_plates_query if
                             element.plate_type is not None]
        for obj in result_list:
            if obj['plate_type'] in eaten_plate_types:
                obj['is_eaten'] = True


async def set_plate_type(result_list, user_type_plate_date_query):
    if user_type_plate_date_query:
        plate_id_to_value = {obj.plate_id: obj.plate_type for obj in user_type_plate_date_query}
        for element in result_list:
            if element['plate_id'] in plate_id_to_value:
                element['plate_type'] = plate_id_to_value[element['plate_id']]


async def put_chosen_plate_to_0_index_if_exists(result_list, chosen_plate):
    if chosen_plate is not None:
        index = None
        for i, obj in enumerate(result_list):
            if obj['plate_id'] == chosen_plate.plate_id:
                index = i
                break
        
        # Check if the dictionary is in the list
        if index is not None:
            # Remove the dictionary from its current position
            removed_dict = result_list.pop(index)
            
            # Insert it at position 0
            result_list.insert(0, removed_dict)
        else:
            # If the dictionary is not in the list, insert None at position 0
            result_list.insert(0, None)
    else:
        # If the dictionary is not in the list, insert None at position 0
        result_list.insert(0, None)


async def set_in_favorites_true_for_plates_in_result_list(result_list, all_favorites_query):
    if all_favorites_query and result_list:
        favorite_plate_ids = [int(element.plate_id) for element in all_favorites_query if
                              element.plate_id is not None]
        for obj in result_list:
            if int(obj['plate_id']) in favorite_plate_ids:
                obj['in_favorites'] = True


async def restore_duplicate_plate_if_exists(result_list, plate_ids):
    try:
        if len(result_list) < 3:
            existing_plate_types = [element['plate_type'] for element in result_list]
            lacking_plate_type_as_list = [element for element in ['Завтрак', 'Обед', 'Ужин'] if
                                          element not in existing_plate_types]
            
            for lacking_plate_type in lacking_plate_type_as_list:
                for element in result_list:
                    
                    if plate_ids.count(element['plate_id']) > 1:
                        result_list.insert(0, element.copy())
                        result_list[0]['plate_type'] = lacking_plate_type
                        
                        plate_ids.remove(element['plate_id'])  # remove this plate_id from ids to avoid infinite loop
                        break
    
    except Exception as x:
        logger.exception(x)
        

get_recipe_db_func_dict = {
    'mysql': """GROUP_CONCAT(CONVERT(measure, CHAR) SEPARATOR ', ') as ingredients_measures,
             GROUP_CONCAT(CONVERT(ingredient_name, CHAR) SEPARATOR ', ') as ingredients,
             GROUP_CONCAT(CONVERT(amount, CHAR) SEPARATOR ', ') as ingredients_amounts""",
    
    'postgresql': """string_agg(cast(measure as text), ', ') as ingredients_measures,
                    string_agg(cast(ingredient_name as text), ', ') as ingredients,
                    string_agg(cast(amount as text), ', ') as ingredients_amounts"""
}


async def get_recipe_values(session, plate_id, tg_id):
    sql_query = text(f"""
    select meal_id, recipe, recipe_time, recipe_active_time, plate_name, meal_name,
    {get_recipe_db_func_dict[os.getenv('DB_ENGINE')]}
    from
    
    (select meal_id, ingredient_name, amount, recipe, recipe_time, recipe_active_time, measure, plate_name, meal_name
    from plates
    inner join plate_meals_association using(plate_id)
    inner join meals using(meal_id)
    inner join meal_ingredients_association using(meal_id)
    inner join ingredients using(ingredient_id)
    where plate_id = {plate_id}) as q
    
    group by meal_id, recipe, recipe_time, recipe_active_time, plate_name, meal_name;
    """)
    
    user = await session.get(models.Ingredient, tg_id)
    multiplier = multiplier_by_plate_diameter[user.plate_diameter]
    
    # Execute the query
    result_query = await session.execute(sql_query)
    result = result_query.fetchall()
    
    meals = list()
    result_dict = dict()
    print(result)
    
    if result:
        result_dict['plate_name'] = result[0].plate_name
        for row in result:

            ingredients = list()
            ingredients_names = row.ingredients.split(', '),
            ingredients_measures = row.ingredients_measures.split(', '),
            ingredients_amounts = row.ingredients_amounts.split(', '),
            
            for ingredient_name, ingredient_measure, ingredient_amount in zip(ingredients_names[0],
                                                                              ingredients_measures[0],
                                                                              ingredients_amounts[0]):
                ingredients.append({
                    'ingredient_name': ingredient_name,
                    'ingredient_measure': ingredient_measure,
                    'ingredient_amount': ingredient_amount * multiplier
                })
            
            meals.append({
                'meal_name': row.meal_name,
                'ingredients': ingredients,
                'recipe': row.recipe,
                'recipe_time': row.recipe_time,
                'recipe_active_time': row.recipe_active_time
            })
        
        result_dict['meals'] = meals
        
        return result_dict
    
    return None
    

async def get_day_word_according_to_number(number):
    number_as_str = str(number)
    if number in ['11', '12', '13', '14']:
        return 'дней'
    elif number_as_str[-1] == '1':
        return 'день'
    elif number_as_str[-1] in ['2', '3', '4']:
        return 'дня'
    else:
        return 'дней'


async def get_coin_word_according_to_number(number):
    number_as_str = str(number)
    if number in ['11', '12', '13', '14']:
        return 'ЖИРкоинов'
    elif number_as_str[-1] == '1':
        return 'ЖИРкоин'
    elif number_as_str[-1] in ['2', '3', '4']:
        return 'ЖИРкоина'
    else:
        return 'ЖИРкоинов'

