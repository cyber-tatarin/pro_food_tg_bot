import os

from aiohttp import web
from sqlalchemy import text

from root.tg.main import admin_ids


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
        print(x)
        raise web.HTTPForbidden()


meal_db_func_dict = {
    'mysql': "GROUP_CONCAT(meal_name SEPARATOR ', ')",
    'postgresql': "string_agg(meal_name, ', ')"
}

percentage_db_func_dict = {
    'mysql': "GROUP_CONCAT(CONVERT(percentage, CHAR) SEPARATOR ', ')",
    'postgresql': "string_agg(cast(percentage as text), ', ')"
}


async def get_nutrient_for_plates_by_ids(session, plate_ids=None, in_json=False) -> list:
    if plate_ids:
        plate_ids_as_str = ', '.join([str(x) for x in plate_ids])
    else:
        plate_ids_as_str = ''
    
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
      {'where plates.plate_id in (' + plate_ids_as_str + ')' if plate_ids else ''}
      group by meals.meal_id, plates.plate_id, meal_name, plate_name, plate_type, recipe_time, recipe_active_time,
      recipe_difficulty, percentage
      order by percentage
    ) as q1

    group by plate_name, plate_type, plate_id;
    """)
    
    # Execute the query
    result = session.execute(sql_query).fetchall()
    
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
                    'calories': int(row.calories),
                    'proteins': int(row.proteins),
                    'fats': int(row.fats),
                    'carbohydrates': int(row.carbohydrates),
                    'in_favorites': False
                })
        
        return result_list


async def set_is_eaten_true_for_plates_in_result_list(result_list, all_today_has_eaten_plates_query):
    if all_today_has_eaten_plates_query:
        eaten_plate_ids = [int(element.plate_id) for element in all_today_has_eaten_plates_query if
                           element.plate_id is not None]
        for obj in result_list:
            if int(obj['plate_id']) in eaten_plate_ids:
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
    if all_favorites_query:
        favorite_plate_ids = [int(element.plate_id) for element in all_favorites_query if
                              element.plate_id is not None]
        for obj in result_list:
            if int(obj['plate_id']) in favorite_plate_ids:
                obj['in_favorites'] = True


async def restore_duplicate_plate_if_exists(result_list, plate_ids):
    if len(result_list) < 3:
        existing_plate_types = [element['plate_type'] for element in result_list]
        lacking_plate_type_as_list = [element for element in existing_plate_types if element not in ['Завтрак', 'Обед', 'Ужин']]
        
        for lacking_plate_type in lacking_plate_type_as_list:
            for element in result_list:
                if plate_ids.count(element['plate_id']) > 1:
                    result_list.insert(0, element.copy())
                    result_list[0]['plate_type'] = lacking_plate_type
                    lacking_plate_type_as_list.remove(lacking_plate_type)
                    plate_ids.remove(element['plate_id'])  # remove this plate_id from ids to avoid infinite loop
                
        
        # index = 0
        # while index < len(result_list):
        #     plate_id = result_list[index]['plate_id']
        #     if plate_ids.count(plate_id) > 1:
        #         result_list.insert(0, result_list[index].copy())
        #         result_list[0]['plate_type'] = plate_type_as_list[0]
        #         plate_type_as_list.pop(0)
        #         plate_ids.remove(plate_id)  # remove this plate_id from ids to avoid infinite loop
        #     index += 1
        
        
        