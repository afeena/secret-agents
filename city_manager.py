import aiohttp
import json
import asyncio
import math


class CityManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.city_list = {}

    async def get_city_coordinates(self, city):
        with aiohttp.ClientSession() as session:
            response = await session.get(
                'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (city, self.api_key))
            try:
                result = await response.json()
            except json.decoder.JSONDecodeError as e:
                print(e)
            else:
                if result['status'] == "OK":
                    coordinates = [result["results"][0]["geometry"]["location"]["lat"],
                                   result["results"][0]["geometry"]["location"]["lng"]]
                    return coordinates
                elif result["status"] == "ZERO_RESULTS":
                    return None
            finally:
                response.release()

    async def add_or_update_city(self, city):
        if city not in list(self.city_list.keys()):
            coordinates = await self.get_city_coordinates(city)
            if coordinates is None:
                return None
            self.city_list[city] = {"lat": coordinates[0], "lng": coordinates[1], "links": 1}
        else:
            self.city_list[city]["links"] += 1
        return 1

    async def unlink_city(self, city):
        self.city_list[city]["links"] -= 1
        if self.city_list[city]["links"] == 0:
            del self.city_list[city]

    async def upload_cities(self, cities):
        for city in cities:
            await self.add_or_update_city(city)

    @staticmethod
    async def calculate_distance(origin, destination):
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

    async def find_nearest_city(self, origin_name):
        origin = self.city_list[origin_name]
        nearest_city = None
        min_dist = float('inf')
        for city_name, value in self.city_list.items():
            dist = await self.calculate_distance(origin, self.city_list[city_name])
            if min_dist > dist and dist != 0:
                min_dist = dist
                nearest_city = city_name
            elif min_dist > dist and dist == 0 and origin["links"] > 1:
                min_dist = dist
                nearest_city = city_name
        return nearest_city, min_dist
