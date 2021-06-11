from flask import Flask, request, Response, abort
from apscheduler.schedulers.background import BackgroundScheduler
from redisDB import RedisDB
from invalidProxiesChecker import InvalidProxiesChecker
from configuration import COUNTRIES, FLASK_HOST

app = Flask(__name__)

redisDb = RedisDB()
invalidProxiesChecker = InvalidProxiesChecker()
scheduler = BackgroundScheduler()
scheduler.add_job(func=invalidProxiesChecker.check_invalid_expiration, trigger="interval", seconds=30)
scheduler.start()

redisDb.load_data()


@app.route('/')
def home():
    return "Proxy Rotator Web Server"


@app.route('/GetProxy/<string:country>', methods=["GET"])
def get_proxy(country):
    if country not in COUNTRIES:
        abort(400, description="No such country code in DB")
    proxyAddress = redisDb.get_next_proxy_by_country(country)
    if not proxyAddress:
        abort(400, description="No available proxy for the country at the moment")
    return Response({proxyAddress}, status=200)


@app.route('/ReportError', methods=["POST"])
def report_error():
    address = request.json["address"]
    country = request.json["country"]
    result = redisDb.mark_proxy_invalid(address, country)
    if result == 1:
        return Response({"The proxy was marked invalid for 6 hours"}, status=200)
    abort(400, description="The proxy does not exist in DB or already have been marked invalid")


if __name__ == "__main__":
    app.run(host=FLASK_HOST)
