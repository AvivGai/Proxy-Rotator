import os
import json
import redisDB


def insert_proxies_to_db():
    if not redisDB.is_db_initialized():
        redisDB.set_initialization_key()
        filename = os.path.join('static', 'MOCK_PROXIES_DATA.json')

        with open(filename) as test_file:
            data = json.load(test_file)

        for i in data:
            address = i["ip_address"]
            country = i["country"]
            redisDB.add_proxy_to_db(address, country)


if __name__ == "__main__":
    insert_proxies_to_db()
