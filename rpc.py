from aiohttp_jrpc import Service
from agent_proxy import AgentProxy


class Rpc(Service):
    @Service.valid({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "city": {"type": "string"},
        },
    })
    async def add(self, ctx, data):
        result = await AgentProxy.agent_manager.add_agent(data["name"], data["city"])
        return result

    @Service.valid({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
        },
    })
    async def where(self, ctx, data):
        result = await AgentProxy.agent_manager.get_agent(data["name"])
        return result

    @Service.valid({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
        },
    })
    async def help(self, ctx, data):
        result = await AgentProxy.agent_manager.find_helpers(data["name"])
        return result

    @Service.valid({
        "type": "object",
        "properties": {
            "filename": {"type": "string"},
        },
    })
    async def save(self, ctx, data):
        result = await AgentProxy.agent_manager.save_agents('agents.csv')
        return result
