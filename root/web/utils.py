from aiohttp import web
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

