#!/usr/bin/env python3
# 
import argparse
import csv
import datetime
import requests
import re
import urllib.parse
from ratelimit import limits, sleep_and_retry

parser = argparse.ArgumentParser(description='downloads historical coin pricing from coingecko.')
parser.add_argument('--coin', help='what coin should we get', required=True)
parser.add_argument('--currency', default='usd', help='What currency should we download things as')
parser.add_argument(
        '--start_date',
        type=lambda s: datetime.datetime.strptime(s, r'%Y-%m-%d'),
        help='Start date yyyy-mm-dd',
        required=True
)
parser.add_argument(
        '--end_date',
        type=lambda s: datetime.datetime.strptime(s, r'%Y-%m-%d'),
        help='End date yyyy-mm-dd', 
        required=True
)

REQUESTS_PER_MINUTE = 15.0

@sleep_and_retry
@limits(calls=1, period=60.0 / REQUESTS_PER_MINUTE)
def fetch(coin, date, currency):
    #quick and dirty injection protection
    assert re.match('^[a-zA-Z-_0-9]+$', coin)
    date_str = date.strftime(r'%d-%m-%Y')
    
    url = 'https://api.coingecko.com/api/v3/coins/%s/history?' % coin + urllib.parse.urlencode({'date' : date_str})
    data = requests.get(url).json()
    return data['market_data']['current_price']['usd']


def output_daterange(coin, currency, start_date, end_date):
    delta = end_date - start_date   # returns timedelta

    for i in range(delta.days + 1):
        day = start_date + datetime.timedelta(days=i)
        try:
            price = fetch(coin, day, currency)
        except:
            price = 0.0
        print('%s, %s' % (day.strftime(r'%Y-%m-%d'), price))

if __name__ == '__main__':
    args = parser.parse_args()
    print('date,price')
    output_daterange(args.coin, args.currency, args.start_date, args.end_date)
