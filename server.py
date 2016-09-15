import asyncio
import os
import json

from aiohttp import web
from agent_proxy import AgentProxy
from rpc import Rpc
from config import Config


class SecretAgentsWeb(web.Application):
    def __init__(self, loop):
        super().__init__(loop=loop)

        self.router.add_route('POST', "/api", Rpc)
        self.router.add_route('POST', "/upload", self.upload_handler)
        public_folder = os.path.join(os.getcwd(), 'public')
        web_folder = os.path.join(os.getcwd(), 'web')
        if not os.path.exists(public_folder):
            os.mkdir(public_folder)

        self.router.add_static("/public", public_folder)
        self.router.add_static("/web", web_folder)
        self.router.add_route('GET', '/', self.show_console)

    async def show_console(self, request):
        with open('web/index.html', mode='rb') as index_page:
            return web.Response(content_type='text/html', body=index_page.read())

    async def upload_handler(self, request):
        data = await request.post()
        csv = data["csv"]
        csv_file = csv.file
        content = csv_file.read()
        result = await AgentProxy.agent_manager.upload_agents(content.decode('utf-8').split('\n'))
        return web.Response(content_type='application/json', body=json.dumps({"count": result}).encode('utf-8'))


async def init(loop):
    app = SecretAgentsWeb(loop)
    interface = Config.config["server"]["interface"]
    port = Config.config["server"]["port"]
    srv = await loop.create_server(app.make_handler(), interface, port)
    print("Server started at %s:%s" % (interface, str(port)))
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(AgentProxy.agent_manager.end_seans())
    pass
