#!/usr/bin/python
import random
import requests
import uuid
import json
from proxychecker import proxylistcheck
import sys
import time


def clean_ascii(text):
    result = ''.join([i if ord(i) < 128 else ' ' for i in text])
    return result.strip()


def clean_numeric(s):
    return int(''.join(i for i in s if i.isdigit()))

total_cars = 0

http_proxies = proxylistcheck('plist.txt', 1)
http_proxy = random.choice(http_proxies)

proxy_dict = {
    "http": http_proxy
}

identifier = uuid.uuid4()
params = {
    'CatID': 1,
    #AreaID: 5.0 == Haifa Area
    'AreaID': 5.0,
    'Auto': 0.0,
    'SubModelID': 1700.0,
    'SubCatID': 1,
    'ModelID': 44.0,
    'FromPrice': 33000,
    'ToPrice': 45000,
    'fromEngineVal': 1200,
    'untilEngineVal': 1210,
    'FromYear': 2011.0,
    'UntilYear': 2014.0,
    'fromHand': 1.0,
    'Hand': 2.0,
    'AppType': 'Android',
    'AppVersion': 2.9,
    'DeviceType': 'Nexus 5',
    'udid': identifier,
    'OSVersion': 5.1,
}

headers = {
    'User-Agent': 'Apache-HttpClient/UNAVAILABLE (java 1.4)'
}

def get_cars(page, model):

    model['Page'] = page + 1.0
    r = requests.get('http://m.yad2.co.il/API/MadorResults.php', params=model, headers=headers, proxies=proxy_dict)

    try:
        data = r.json()
    except:
        print r.text
        raise

    private_cars = data['Private']['Results']
    for item in private_cars:

        car_id = clean_ascii(item.get('RecordID', ''))

        if not car_id:
            continue

        price = clean_ascii(item['Line3'])
        price = clean_numeric(price)
        raw = item['Line2']

        raw = raw.encode('ascii', 'ignore')
        raw = clean_ascii(raw)
        raw = ''.join(raw.split())
        raw = raw.split(',:')
        hand = clean_numeric(raw[0])
        year = clean_numeric(raw[1])
        engvolume = clean_ascii(item['Line4'])
        engvolume = clean_numeric(engvolume)
        car_name = item['Line1']

        car_link = 'http://www.yad2.co.il/Cars/Car_info.php?CarID={car_id}'.format(car_id=car_id)

        yield car_id, car_name, price, hand, year, car_link, engvolume

        # Sleep placed for avoiding load on their servers
        # time.sleep(0.3)

def get_num_pages(model):

    for i in xrange(10):
        model['Page'] = i + 1.0
        r = requests.get('http://m.yad2.co.il/API/MadorResults.php', params=model, headers=headers, proxies=proxy_dict)
        try:
            data = r.json()
        except:
            return i

def main():

    global total_cars
    try:
        with open('.data') as f:
            raw = f.read()
            data = json.loads(raw)
    except:
        data = {}

    chevrolet_spark_haifa = dict(params)
    chevrolet_spark_haifa['fromEngineVal'] = 1200
    chevrolet_spark_haifa['untilEngineVal'] = 1210
    chevrolet_spark_haifa['FromPrice'] = 30000
    chevrolet_spark_haifa['ToPrice'] = 45000
    chevrolet_spark_haifa['ModelID'] = 44.0
    chevrolet_spark_haifa['SubModelID'] = 1700.0
    chevrolet_spark_haifa['AreaID'] = 5.0

    chevrolet_spark_krayot = dict(chevrolet_spark_haifa)
    chevrolet_spark_krayot['AreaID'] = 6.0



    car_models = []
    car_models.append(chevrolet_spark_haifa)
    car_models.append(chevrolet_spark_krayot)

    for model in car_models:
        pages = get_num_pages(model)
        for i in xrange(pages):
            for car_id, car_name, price, hand, year, url, engv in get_cars(i, model):
                item = data.get(car_id, {})
                prev_max_price = item.get('max_price', price)
                prev_min_price = item.get('min_price', price)

                item['car_name'] = car_name
                item['price'] = price
                item['max_price'] = max(prev_max_price, price)
                item['min_price'] = min(prev_min_price, price)
                item['hand'] = hand
                item['year'] = year
                item['url'] = url
                item['volume'] = engv

                data[car_id] = item
                total_cars += 1

            with open('f:/yad2/yad2.data', "w+") as w:
                raw = json.dumps(data, indent=4, sort_keys=True)
                w.write(raw)



if __name__ == "__main__":
    while True:
        main()
        print total_cars
        total_cars = 0
        sleep = 300
        print "Sleeping for %d seconds" % sleep
        time.sleep(sleep)
