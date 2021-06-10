from flask import Flask, request, Response
from apscheduler.schedulers.background import BackgroundScheduler
from redisDB import RedisDB
from invalidProxiesChecker import InvalidProxiesChecker

COUNTRIES = ['us', 'uk']

app = Flask(__name__)

redisDb = RedisDB()
invalidProxiesChecker = InvalidProxiesChecker()

scheduler = BackgroundScheduler()
scheduler.add_job(func=invalidProxiesChecker.check_invalid_expiration, trigger="interval", seconds=60)
scheduler.start()

redisDb.load_data()


@app.route('/')
def home():
    return "Proxy Rotator Web Server"


@app.route('/GetProxy/<string:country>', methods=["GET"])
def get_proxy(country):
    if country not in COUNTRIES:
        return Response(status=400)  # no such country code
    proxyAddress = redisDb.get_next_proxy_by_country(country)
    if not proxyAddress:
        return Response(status=404)  # no available proxy for the country at the moment
    return Response({proxyAddress}, status=200)


@app.route('/ReportError', methods=["POST"])
def report_error():
    address = request.json["address"]
    country = request.json["country"]
    result = redisDb.mark_proxy_invalid(address, country)
    if result == 1:
        return Response(status=200)  # proxy was marked as invalid
    return Response(status=400)  # no such country code and ip address combination in db


if __name__ == "__main__":
    app.run(host="localhost")
