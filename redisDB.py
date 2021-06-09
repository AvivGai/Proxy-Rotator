import redis

COUNTRY_CURRENT_INDEX_KEY_PREFIX = "current_index"              #key: "current_index_us"/"current_index_uk"
COUNTRY_PROXY_ADDRESSES_KEY_PREFIX = "country_proxy_addresses"  #key: "country_proxy_addresses_us"/"country_proxy_addresses_uk"
INVALID_PROXY_KEY_PREFIX = "invalid_proxy"                      #key: "invalid_proxy_1.1.1.1_us"

r = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)


def get_current_index_key_by_country(country):
    key = COUNTRY_CURRENT_INDEX_KEY_PREFIX + "_" + country
    return key


def get_proxy_addresses_key_by_country(country):
    key = COUNTRY_PROXY_ADDRESSES_KEY_PREFIX + "_" + country
    return key


def get_invalid_proxy_key_by_address_and_country(address, country):
    key = INVALID_PROXY_KEY_PREFIX + "_" + address + "_"+country
    return key


def get_proxy_key(address, country):
    key = address + "_" + country
    return key


# def get_current_index_by_country(country):
#     key = get_current_index_key_by_country(country)
#     currentIndex = r.get(key)
#     if currentIndex:
#         return int(currentIndex)
#     return 0


def add_proxy_to_db(address, country):
    countryListKey = get_proxy_addresses_key_by_country(country)
    r.rpush(countryListKey, address)
    proxyKey = get_proxy_key(address, country)
    r.set(proxyKey, 1)


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


def get_next_proxy_by_country(country):
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

    addressesListKey = get_proxy_addresses_key_by_country(country)
    nextProxyAddress = r.lpop(addressesListKey)
    invalidKey = get_invalid_proxy_key_by_address_and_country(nextProxyAddress, country)
    r.rpush(addressesListKey, nextProxyAddress)
    if r.exists(invalidKey):
        return 0
    return nextProxyAddress


def mark_proxy_invalid(address, country):
    proxyKey = get_proxy_key(address, country)
    addressesListKey = get_proxy_addresses_key_by_country(country)

    if r.exists(proxyKey):
        invalidKey = get_invalid_proxy_key_by_address_and_country(address, country)
        r.setex(invalidKey, 21600, 1)
        r.lrem(addressesListKey, 1,  address)
        r.rpush(addressesListKey, address)
        return 1
    return 0


def set_initialization_key():
    r.set("initialized", 1)


def is_db_initialized():
    if r.exists("initialized"):
        return True
    return False



