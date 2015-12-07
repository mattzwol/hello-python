import os
import uuid
from flask import Flask,render_template, url_for, request
import redis
import json
import pygeoip

app = Flask(__name__)
my_uuid = str(uuid.uuid1())
BLUE = "#0099FF"
GREEN = "#33CC33"
OTHER = "#840e47"
GREY = '#808080'
pagehit = 0
countrycount = 0
COLOR = OTHER

rediscloud_service = json.loads(os.environ['VCAP_SERVICES'])['rediscloud'][0]
credentials = rediscloud_service['credentials']
hostname = credentials['hostname']
port = credentials['port']
password = credentials['password']
REDIS_SERVER = redis.Redis(host=hostname, port=port, password=password)

@app.route('/')
def hello():
    global pagehit
    client_ip = request.headers.get('X_FORWARDED_FOR', None).split(',')[0]
    gi = pygeoip.GeoIP('GeoIPCity.dat')
    city = gi.record_by_addr(client_ip)['city']
    postcode = gi.record_by_addr(client_ip)['postal_code']
    country = gi.country_name_by_addr(client_ip)
    #country = 'US'
    if country == 'Australia':
            img_url = url_for('static',filename='OzMap2.gif')
    else:
            img_url = url_for('static',filename='worldmap.gif')
    print client_ip
    pagehit = REDIS_SERVER.incr('MattZcounter')
    REDIS_SERVER.sadd("MattZcountrylist", country)
    countrylist = REDIS_SERVER.smembers("MattZcountrylist")
    countrycount = len(countrylist)
    starwars = url_for('static',filename='starwars.gif')
    # countrycount = 6
    if countrycount < 10:
        return render_template('index.html', bgcolor=COLOR, country=country, client_ip=client_ip, city=city, pagehit=pagehit, img_url=img_url, postcode=postcode, countrylist=countrylist, countrycount=countrycount)
    else:
        return render_template('index2.html', bgcolor=GREY, country=country, client_ip=client_ip, city=city, pagehit=pagehit, img_url=starwars, postcode=postcode, countrylist=countrylist, countrycount=countrycount)
if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
