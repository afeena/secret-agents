import asyncio
import os
import json

from aiohttp import web
from agent_proxy import AgentProxy
from rpc import Rpc


async def upload_handler(request):
    data = await request.post()
    csv = data["csv"]
    csv_file = csv.file
    content = csv_file.read()
    result = await AgentProxy.agent_manager.upload_agents(content.decode('utf-8').split('\n'))
    return web.Response(content_type='application/json', body=json.dumps({"count": result}).encode('utf-8'))


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('POST', "/api", Rpc)
    app.router.add_route('POST', "/upload", upload_handler)
    public_folder = os.path.join(os.getcwd(), 'public')
    web_folder = os.path.join(os.getcwd(), 'web')
    if not os.path.exists(public_folder):
        os.mkdir(public_folder)

    app.router.add_static("/public", public_folder)
    app.router.add_static("/", web_folder)
    srv = await loop.create_server(app.make_handler(),
                                   "0.0.0.0", 8080)
    print("Server started at http://0.0.0.0:8080")
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(AgentProxy.agent_manager.end_seans())
    pass
