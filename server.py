import asyncio
import os
from aiohttp import web
import json
from multidict import MultiDict
from aiohttp_jrpc import Service, JError, jrpc_errorhandler_middleware
from agent_manager import AgentManager

agent_manager = AgentManager()


class MyJRPC(Service):
    @Service.valid({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "city": {"type": "string"},
        },
    })
    async def add(self, ctx, data):
        result = await agent_manager.add_agent(data["name"], data["city"])
        return result

    @Service.valid({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
        },
    })
    async def where(self, ctx, data):
        result = await agent_manager.get_agent(data["name"])
        return result

    @Service.valid({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
        },
    })
    async def help(self, ctx, data):
        result = await agent_manager.find_helpers(data["name"])
        return result

    @Service.valid({
        "type": "object",
        "properties": {
            "filename": {"type": "string"},
        },
    })
    async def save(self, ctx, data):
        result = await agent_manager.save_agents('agents.csv')
        return result


async def upload_handler(request):
    data = await request.post()
    csv = data["csv"]
    csv_file = csv.file
    content = csv_file.read()
    result = await agent_manager.upload_agents(content.decode('utf-8').split('\n'))
    return web.Response(content_type='application/json', body=json.dumps({"count": result}).encode('utf-8'))


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('POST', "/api", MyJRPC)
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
    loop.run_until_complete(agent_manager.end_seans())
    pass
