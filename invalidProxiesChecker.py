from redisDB import RedisDB, INVALID_PROXY_KEY
import time


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
        countryListKey = self.r.get_proxy_addresses_key_by_country(country)
        self.r.rpush_to_list(countryListKey, address)

    def check_invalid_expiration(self):
        timestamp = 0
        while float(timestamp) < time.time():
            proxy = self.r.lpop_from_list(INVALID_PROXY_KEY)
            if not proxy:
                break
            proxyParameters = proxy.split("_")
            timestamp = self.get_proxy_timestamp(proxyParameters)
            if float(timestamp) < time.time():
                self.make_proxy_valid_again(proxyParameters)
            else:
                self.r.lpush_to_list(proxy)
                break
