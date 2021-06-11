# Proxy-Rotator
A web server app to get proxy IP address by country code. The server returns proxies from DB in a round robin order. The server also support reporting a proxy as invalid, and after that the reported proxy will not be returned for 6 hours.
## Technologies Used:
* Code written in Python
* Flask framework
* Redis as DB

## Usage:
Clone the repository and cd into it:
```bash
git clone https://github.com/AvivGai/Proxy-Rotator.git
cd Proxy-Rotator
```
Create virtual environment and activate it:
```bash
python3 -m venv venv
. venv/bin/activate
```
Install requirements:
```bash
pip install flask
pip install apscheduler
pip install redis
```
Run the project:
```bash
python app.py
```

## Supported Requests:
1. HTTP GET: /GetProxy - gets a country code (‘us’\ ‘uk’) and returns a proxy from the list

GET request to http://localhost:5000/GetProxy/<country_code>
2. HTTP POST: /ReportError - Gets an IP address and a country code and marks it as invalid for the next 6 hours.

POST request to http://localhost:5000/GetProxy/ReportError with json body: {"address":"x.x.x.x", "country":"country_code"} 


### Possible improvements (if had more time) :
* Run the project with Docker instead of running it locally.
* Use Celery worker to run a background job instead of using BackgroundScheduler (from apscheduler).
* Distrbute the system on a number of servers.
* Maybe figure out if there is a way to report a proxy as invalid in O(1) (in current implementaion GetProxy is O(1) and ReportError is O(n) where n is the number of proxies in the country list).
