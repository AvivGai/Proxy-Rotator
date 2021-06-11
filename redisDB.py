import redis
import time
import os
import json
from configuration import *


class RedisDB:

    def __init__(self):
        self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    def get_addresses_key_by_country(self, country):
        key = COUNTRY_PROXY_ADDRESSES_KEY_PREFIX + "_" + country
        return key

    def get_invalid_proxies_key(self):
        return INVALID_PROXY_KEY

    def get_proxy_key(self, address, country):
        key = address + "_" + country
        return key

    def rpush_to_list(self, key, value):
        self.r.rpush(key, value)

    def lpop_from_list(self, key):
        return self.r.lpop(key)

    def lpush_to_list(self, key, value):
        self.r.lpush(key, value)

    def set_initialization_key(self):
        self.r.set("initialized", 1)

    def is_db_initialized(self):
        if self.r.exists("initialized"):
            return True
        return False

    def add_proxy_to_db(self, address, country):
        countryProxiesListKey = self.get_addresses_key_by_country(country)
        self.r.rpush(countryProxiesListKey, address)
        proxyKey = self.get_proxy_key(address, country)
        self.r.set(proxyKey, 1)  # add address+country combination to db

    def load_data(self):
        if not self.is_db_initialized():
            self.set_initialization_key()
            filename = os.path.join('static', DATA_FILE_NAME)
            with open(filename) as test_file:
                data = json.load(test_file)
            for i in data:
                address = i["ip_address"]
                country = i["country"]
                self.add_proxy_to_db(address, country)

    def get_next_proxy_by_country(self, country):
        countryProxiesListKey = self.get_addresses_key_by_country(country)
        nextProxyAddress = self.r.lpop(countryProxiesListKey)
        if nextProxyAddress:
            self.r.rpush(countryProxiesListKey, nextProxyAddress)  # return proxy to the end of the list
        return nextProxyAddress

    def mark_proxy_invalid(self, address, country):
        proxyKey = self.get_proxy_key(address, country)
        result = 0
        if self.r.exists(proxyKey):
            countryProxiesListKey = self.get_addresses_key_by_country(country)
            result = self.r.lrem(countryProxiesListKey, 1, address)
            if result == 1:
                invalidProxiesKey = self.get_invalid_proxies_key()
                invalidExpirationTime = time.time() + INVALID_TIME_IN_SEC
                value = country + "_" + address + "_" + str(invalidExpirationTime)  # for example: "us_1.1.1.1_524786"
                self.r.rpush(invalidProxiesKey, value)
        return result  # proxy does not exist in DB or already marked invalid
