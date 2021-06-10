import redis
import time
import os
import json

# INVALID_PROXY_KEY_PREFIX = "invalid_proxy"
# COUNTRY_CURRENT_INDEX_KEY_PREFIX = "current_index"              #key: "current_index_us"/"current_index_uk"
COUNTRY_PROXY_ADDRESSES_KEY_PREFIX = "country_proxy_addresses"  # key: "country_proxy_addresses_us"/"country_proxy_addresses_uk"
INVALID_PROXY_KEY = "invalid_proxies"  # key: "invalid_proxy_1.1.1.1_us"
INVALID_TIME_SEC = 10
REDIS_HOST = "localhost"
REDIS_PORT = 6379


class RedisDB:

    def __init__(self):
        self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    # def get_current_index_key_by_country(self, country):
    #     key = COUNTRY_CURRENT_INDEX_KEY_PREFIX + "_" + country
    #     return key

    def get_proxy_addresses_key_by_country(self, country):
        key = COUNTRY_PROXY_ADDRESSES_KEY_PREFIX + "_" + country
        return key

    # def get_invalid_proxies_key_by_address_and_country(self, address, country):
    #     key = INVALID_PROXY_KEY_PREFIX + "_" + address + "_"+country
    #     return key

    def get_invalid_proxies_key(self):
        return INVALID_PROXY_KEY

    def get_proxy_key(self, address, country):
        key = address + "_" + country
        return key

    def get_invalid_proxies_key(self):
        return INVALID_PROXY_KEY

    def rpush_to_list(self, key, value):
        self.r.rpush(key, value)

    def lpop_from_list(self, key):
        return self.r.lpop(key)

    def lpush_to_list(self, key, value):
        self.r.lpush(key, value)
    # def get_current_index_by_country(country):
    #     key = get_current_index_key_by_country(country)
    #     currentIndex = r.get(key)
    #     if currentIndex:
    #         return int(currentIndex)
    #     return 0

    def add_proxy_to_db(self, address, country):
        # add to the country list
        countryProxiesListKey = self.get_proxy_addresses_key_by_country(country)
        self.r.rpush(countryProxiesListKey, address)
        # add address+country combinatio to db
        proxyKey = self.get_proxy_key(address, country)
        self.r.set(proxyKey, 1)

        # self.r.zadd(countryListKey, {address: time.time()})

    # def increment_index(country):
    #     countryCurrentIndex = get_current_index_by_country(country)
    #     countryListKey = get_proxy_addresses_key_by_country(country)
    #     countryListLength = r.llen(countryListKey)
    #     if countryCurrentIndex == countryListLength - 1:
    #         reset_index(country)
    #     else:
    #         key = get_current_index_key_by_country(country)
    #         r.incr(key)

    # def reset_index(country):
    #     key = get_current_index_key_by_country(country)
    #     r.delete(key)

    def get_next_proxy_by_country(self, country):
        # currentIndex = get_current_index_by_country(country)
        # addressesListKey = get_proxy_addresses_key_by_country(country)
        # nextProxyAddress = r.lindex(addressesListKey, currentIndex)
        # increment_index(country)
        #
        # counter = 0
        # invalidAddressKey = get_invalid_proxy_key_by_address_and_country(nextProxyAddress, country)
        # while r.exists(invalidAddressKey) and counter < 20:
        #     currentIndex = get_current_index_by_country(country)
        #     nextProxyAddress = r.lindex(addressesListKey, currentIndex)
        #     increment_index(country)
        #     counter += 1
        #
        # return nextProxyAddress

        countryProxiesListKey = self.get_proxy_addresses_key_by_country(country)
        nextProxyAddress = self.r.lpop(countryProxiesListKey)
        # invalidKey = get_invalid_proxy_key_by_address_and_country(nextProxyAddress, country)
        if nextProxyAddress:
            self.r.rpush(countryProxiesListKey, nextProxyAddress)  # return proxy to the end of the list
        # if r.exists(invalidKey):
        #     return 0
        # return nextProxyAddress
        #
        # nextProxyAddress = self.r.zrange(addressesListKey, 0, 0)[0]
        # timestamp = self.r.zscore(addressesListKey, nextProxyAddress)
        # if timestamp < time.time():
        #     self.r.zadd(addressesListKey, {nextProxyAddress: time.time()})
        return nextProxyAddress
        # return 0

    def mark_proxy_invalid(self, address, country):
        proxyKey = self.get_proxy_key(address, country)

        if self.r.exists(proxyKey):
            # invalidKey = get_invalid_proxy_key_by_address_and_country(address, country)
            # r.setex(invalidKey, 21600, 1)
            # r.lrem(addressesListKey, 1,  address)
            # r.rpush(addressesListKey, address)
            countryProxiesListKey = self.get_proxy_addresses_key_by_country(country)
            self.r.lrem(countryProxiesListKey, 1, address)  # todo: maybe sheck if was actually removed and respond accordingly
            invalidProxiesKey = self.get_invalid_proxies_key()
            invalidExpirationTime = time.time() + INVALID_TIME_SEC
            value = country + "_" + address + "_" + str(invalidExpirationTime)
            self.r.rpush(invalidProxiesKey, value)
            return 1
        return 0

    def set_initialization_key(self):
        self.r.set("initialized", 1)

    def is_db_initialized(self):
        if self.r.exists("initialized"):
            return True
        return False

    def load_data(self):
        if not self.is_db_initialized():
            self.set_initialization_key()
            filename = os.path.join('static', 'MOCK_PROXIES_DATA_7.json')

            with open(filename) as test_file:
                data = json.load(test_file)

            for i in data:
                address = i["ip_address"]
                country = i["country"]
                self.add_proxy_to_db(address, country)


