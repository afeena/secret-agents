import aiohttp
import json
import math


class CityError(Exception):
    pass


class CityManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.city_list = {}

    async def add_or_update_city(self, city):
        if city not in list(self.city_list.keys()):
            try:
                await self.check_city(city)
            except CityError:
                raise
            else:
                await self.calculate_nearest_city(city)
                self.city_list[city]["links"] = 1
        else:
            self.city_list[city]["links"] += 1

    async def unlink_city(self, city):
        self.city_list[city]["links"] -= 1
        if self.city_list[city]["links"] == 0:
            del self.city_list[city]

    async def upload_cities(self, cities):
        for city in cities:
            await self.add_or_update_city(city)

    async def check_city(self, city):
        with aiohttp.ClientSession() as session:
            response = await session.get(
                'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'
                % (city, self.api_key)
            )
            try:
                result = await response.json()
            except json.decoder.JSONDecodeError as e:
                print(e)
            else:
                if result["status"] != "OK":
                    raise CityError
                else:
                    lat = result["results"][0]["geometry"]["location"]["lat"]
                    lng = result["results"][0]["geometry"]["location"]["lng"]
                    self.city_list[city] = {}
                    self.city_list[city]["coordinates"] = {"lat": lat, "lng": lng}

    async def calculate_nearest_city(self, origin):
        nearest_city = None
        min_dist = float('inf')
        destinations = list(self.city_list.keys())
        destinations = [x for x in destinations if x != origin]

        if destinations:
            dst_str = '|'.join(destinations)
            with aiohttp.ClientSession() as session:
                response = await session.get(
                    'https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&key=%s'
                    % (origin, dst_str, self.api_key)
                )
                try:
                    result = await response.json()
                except json.decoder.JSONDecodeError as e:
                    print(e)
                else:
                    if result["rows"][0]["elements"][0]["status"] != "OK":
                        nearest_city, min_dist = await self.alternative_nearest(origin, destinations)
                    else:
                        for (dst, distance) in zip(destinations, result["rows"][0]["elements"]):
                            if min_dist > distance["distance"]["value"]:
                                min_dist = distance["distance"]["value"]
                                nearest_city = dst
                    if self.city_list[nearest_city]["nearest_city"][1] > min_dist:
                        self.city_list[nearest_city]["nearest_city"] = (origin, min_dist)
        self.city_list[origin]["nearest_city"] = (nearest_city, min_dist)

    async def alternative_nearest(self, origin, destination):
        nearest_city = None
        min_dist = float('inf')

        for dst in destination:
            distance = await self.distance_calculate(self.city_list[origin]["coordinates"],
                                                     self.city_list[dst]["coordinates"])
            if min_dist > distance:
                min_dist = distance
                nearest_city = dst
        return nearest_city, min_dist

    async def distance_calculate(self, origin, destination):
        earth_radius = 6378.137e3  # use Equatorial radius
        lat1 = math.radians(origin["lat"])
        lat2 = math.radians(destination['lat'])
        delta_lat = math.radians(destination['lat'] - origin["lat"])
        delta_lng = math.radians(destination['lng'] - origin["lng"])

        a = math.sin(delta_lat / 2) * math.sin(delta_lat / 2) + math.cos(lat1) * math.cos(lat2) * math.sin(
            delta_lng / 2) * math.sin(delta_lng / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt((1 - a)))
        distance = earth_radius * c
        return distance

    async def find_nearest_city(self, city):
        if self.city_list[city]["links"] > 1:
            return city, 0
        else:
            return self.city_list[city]["nearest_city"]
