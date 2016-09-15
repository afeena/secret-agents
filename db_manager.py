import sqlite3
import os


class DBManager:
    def __init__(self, db):
        self.db = db
        self.init_base()

    def init_base(self):
        if not os.path.exists(self.db):
            open(self.db, 'a').close()
            self.execute("CREATE TABLE agents (name text, city text)", tuple())

    def execute(self, query, values, many=False):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        if not many:
            cursor.execute(query, values)
        else:
            cursor.executemany(query, values)
        result = cursor.fetchall()
        connection.commit()
        connection.close()

        return result

    def save_agent(self, agent):
        result = self.execute("INSERT INTO agents VALUES (?,?)", (agent["name"], agent["city"]))
        return result

    def update_agent(self, city, name):
        result = self.execute("UPDATE agents SET city=? WHERE name=?", (city, name))
        return result

    def find_agent_by_name(self, name):
        result = self.execute("SELECT * FROM agents WHERE name=?", (name,))
        return result

    def find_agent_by_city(self, city):
        result = self.execute("SELECT * FROM agents WHERE city=?", (city,))
        return result

    def get_all_agents(self):
        result = self.execute("SELECT * FROM agents", tuple())
        return result

    def load_agents(self, agents):
        result = self.execute("INSERT INTO agents VALUES (?,?)", agents, many=True)
        return result

    def clear_table(self):
        self.execute("DELETE FROM agents", tuple())
