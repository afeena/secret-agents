import os
import csv
import ngram
import pylev
from db_manager import DBManager
from city_manager import CityManager, CityError
from config import Config


class EmptyData(Exception):
    pass


class AgentManager:
    def __init__(self):
        config = Config.config
        self.db_manager = DBManager(config['database']['name'])
        self.city_manager = CityManager(config['google_maps_api']['key'])

    async def validate_data(self, data):
        for data_str in data:
            data_str = data_str.strip()
            if not data_str:
                raise EmptyData

    async def add_agent(self, name, city):
        try:
            await self.validate_data([name, city])
        except EmptyData:
            return "Empty field(s)"
        agent = self.db_manager.find_agent_by_name(name)
        try:
            await self.city_manager.add_or_update_city(city)
        except CityError:
            return "city %s not found. Try another city" % city
        else:
            if not agent:
                self.db_manager.save_agent({"name": name, "city": city})
            else:
                await self.city_manager.unlink_city(agent[0][1])
                self.db_manager.update_agent(city, name)
            return "OK"

    async def suggest_agent(self, name):
        try:
            await self.validate_data([name])
        except EmptyData:
            return "Empty field(s)"
        all_agents = self.db_manager.get_all_agents()
        list_names = [x[0] for x in all_agents]
        ngram_dict = ngram.NGram(list_names)
        possible_suggestions = ngram_dict.search(name)
        for suggested_name in possible_suggestions:
            if pylev.classic_levenshtein(suggested_name[0], name) <= 3:
                return suggested_name[0]

    async def get_agent(self, name):
        try:
            await self.validate_data([name])
        except EmptyData:
            return "Empty field(s)"
        agent = self.db_manager.find_agent_by_name(name)
        if agent:
            return agent[0][1]
        else:
            result = await self.suggest_agent(name)
            if result is not None:
                return '%s not found. \n Suggestion: %s' % (name, result)
            else:
                return '%s not found. \n Nothing to suggest.' % name

    async def find_helpers(self, name):
        try:
            self.validate_data([name])
        except EmptyData:
            return "Empty field(s)"
        agent = self.db_manager.find_agent_by_name(name)
        if not agent:
            result = await self.suggest_agent(name)
            if result is not None:
                return '%s not found. \n Suggestion: %s' % (name, result)
            else:
                return '%s not found. \n Nothing to suggest.' % name
        (nearest_city, distance) = await self.city_manager.find_nearest_city(agent[0][1])
        if nearest_city is not None:
            helpers = self.db_manager.find_agent_by_city(nearest_city)
            helper = [x[0] for x in helpers if x != name]
            return "%s distance: %s km" % (helper[0], str(distance / 1e3))
        else:
            return "Nobody helps you"

    async def upload_agents(self, file):
        agent_reader = csv.reader(file, delimiter=',', quotechar='|')
        next(agent_reader, None)  # skip headers
        count = 0
        for row in agent_reader:
            if not row:
                continue
            await self.add_agent(row[0], row[1])
            count += 1
        return count

    async def save_agents(self, filename):
        try:
            await self.validate_data([filename])
        except EmptyData:
            return "Empty field(s)"
        agents = self.db_manager.get_all_agents()
        filepath = os.path.normpath(os.path.join('public/', filename))
        if agents:
            with open(filepath, mode='w', encoding='utf-8', newline='') as csvfile:
                agent_writer = csv.writer(csvfile, delimiter=',')
                agent_writer.writerow(['city', 'name'])
                agent_writer.writerows([list(elem) for elem in agents])
        return filepath

    async def end_seans(self):
        self.db_manager.clear_table()
