import os
import aiohttp
from aiohttp import web
import jinja2
import aiohttp_jinja2

from root.db import setup as db
from root.db import models
from root.logger.config import logger
from root.tg.main import admin_ids


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
    
    name = data.get('name')
    
    measure = data.get('measure')
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
    except Exception as x:
        print(x)
    finally:
        if session.is_active:
            session.close()
    
    print(name, measure, calories, proteins, fats, carbohydrates)
    return web.Response(status=200)


@aiohttp_jinja2.template('add_meal.html')
async def add_meal_get(request):
    return {}


async def add_meal_post(request):
    print('Got data')
    data = await request.json()
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
        return
    finally:
        if session1.is_active:
            session1.close()
    print('After 1st block')
    
    session2 = db.Session()
    try:
        for i in range(1, (len(data)-5)//2+1):
            print(i, 'i')
            ingredient_id = data.get(f'ingredient_id{i}')
            ingredient_amount = data.get(f'ingredient_amount{i}')
            
            print(ingredient_id, f'ingredient{1}')

            ingredient = session2.query(models.Ingredient).filter(models.Ingredient.ingredient_id == int(ingredient_id)).first()
            association = models.meal_ingredients_association.insert().values(
                amount=float(ingredient_amount),
                ingredient_id=ingredient.ingredient_id,
                meal_id=int(new_meal_id)
            )
            session2.execute(association)

        session2.commit()
    except Exception as x:
        print('second exception\n\n\n\n')
        print(x)
        pass


@aiohttp_jinja2.template('add_plate.html')
async def add_plate_get(request):
    return {}


async def add_plate_post(request):
    print('Got data')
    data = await request.json()
    print(data)
    print('Parsed data')
    
    name = data.get('name')
    
    session1 = db.Session()
    print('Created session')
    try:
        new_plate = models.Plate(
            plate_name=name,
        )
        print("Created new_meal:", new_plate)
        session1.add(new_plate)
        session1.commit()
        
        session1.refresh(new_plate)
        new_plate_id = new_plate.plate_id
        print("Obtained new_meal_id:", new_plate_id)
    
    except Exception as x:
        print('First exception:', x)
        return
    finally:
        if session1.is_active:
            session1.close()
    print('After 1st block')
    
    session2 = db.Session()
    try:
        for i in range(1, (len(data) - 1) // 2 + 1):
            print(i, 'i')
            meal_id = data.get(f'meal_id{i}')
            meal_percentage = data.get(f'meal_percentage{i}')
            
            meal = session2.query(models.Meal).filter(
                models.Meal.meal_id == int(meal_id)).first()
            association = models.plate_meals_association.insert().values(
                percentage=int(meal_percentage),
                plate_id=int(new_plate_id),
                meal_id=meal.meal_id
            )
            session2.execute(association)
        
        session2.commit()
    except Exception as x:
        print('second exception\n\n\n\n')
        print(x)
        pass


async def is_admin_post(request):
    json_data = request.json()
    tg_id = json_data.get('tg_id')
    if tg_id in admin_ids:
        return web.json_response({'is_admin': 'true'})
    else:
        return web.json_response({'is_admin': 'false'})


app = web.Application()

app.add_routes([
    # web.get('/profile/{user_id}', profile_view),
    web.get('/add_ingredient', add_ingredient_get),
    web.get('/add_meal', add_meal_get),
    web.get('/add_plate', add_plate_get),
                ])

app.add_routes([
    web.post('/api/is_admin', is_admin_post),
    web.post('/api/add_ingredient', add_ingredient_post),
    web.post('/api/add_meal', add_meal_post),
    web.post('/api/add_plate', add_plate_post),
                ])


aiohttp_jinja2.setup(app, loader=env.loader, context_processors=[aiohttp_jinja2.request_processor])

if __name__ == '__main__':
    # web.run_app(app, host='0.0.0.0')
    web.run_app(app, host='127.0.0.1', port=80)
