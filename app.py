from flask import Flask, request, Response
import redisDB
import loadData

app = Flask(__name__)


@app.route('/')
def home():
    return "hello world"


@app.route('/GetProxy/<country>', methods=["GET"])
def get_proxy(country):
    proxyAddress = redisDB.get_next_proxy_by_country(country)
    return Response({proxyAddress}, status=200)


@app.route('/ReportError', methods=["POST"])
def report_error():
    address = request.json["address"]
    country = request.json["country"]
    result = redisDB.mark_proxy_invalid(address, country)
    if result == 1:
        return Response(status=200)
    return Response(status=400)


if __name__ == "__main__":
    loadData.insert_proxies_to_db()
    app.run(debug=True, host="0.0.0.0")
