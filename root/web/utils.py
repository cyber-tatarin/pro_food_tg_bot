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


async def get_nutrient_for_plates_by_ids(session, plate_ids=None) -> list:
    plate_ids_as_str = ', '.join([str(x) for x in plate_ids])
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
    return result
