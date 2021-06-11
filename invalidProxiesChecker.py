import time
from redisDB import RedisDB
from configuration import INVALID_PROXY_KEY


class InvalidProxiesChecker:

    def __init__(self):
        self.r = RedisDB()

    def get_proxy_country(self, proxyParametersList):
        return proxyParametersList[0]

    def get_proxy_address(self, proxyParametersList):
        return proxyParametersList[1]

    def get_proxy_timestamp(self, proxyParametersList):
        return proxyParametersList[2]

    def make_proxy_valid_again(self, proxyParametersList):
        country = self.get_proxy_country(proxyParametersList)
        address = self.get_proxy_address(proxyParametersList)
        countryListKey = self.r.get_addresses_key_by_country(country)
        self.r.rpush_to_list(countryListKey, address)

    def check_invalid_expiration(self):
        timestamp = 0
        while float(timestamp) < time.time():
            proxyToCheck = self.r.lpop_from_list(
                INVALID_PROXY_KEY)  # proxy format: "us_1.1.1.1_524786" (country_address_invalidExpirationTime)
            if not proxyToCheck:
                break
            proxyParameters = proxyToCheck.split("_")
            timestamp = self.get_proxy_timestamp(proxyParameters)
            if float(timestamp) < time.time():
                self.make_proxy_valid_again(proxyParameters)
            else:
                self.r.lpush_to_list(proxyToCheck)  # return proxy to the head of the list
                break  # since we are pushing invalid proxies to the end of the list, they are sorted by time,
                # so i the first one is not valid there is no point to check the rest
