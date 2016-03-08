#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import re
from urllib.request import urlopen
from urllib.parse import urlencode

try:
    import config as config_
except ImportError:
    pass
class ConfigProxy():
    def __getattr__(self, key):
        try:
            return getattr(config_, key)
        except NameError:
            pass
        except AttributeError:
            pass
config = ConfigProxy()

def read_config():
    ns = argparse.Namespace()
    ns.location = config.LOCATION
    ns.unit = config.UNIT
    return ns

def parse_argumnets():
    ns = read_config()

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", help="location",                                   dest="location",     metavar="LOCATION")
    parser.add_argument("-u", help="unit ('c' for Celsius, 'f' for Fahrenheit)", dest="unit",         metavar="UNIT", choices=['f', 'c'],  default='f')
    parser.add_argument("-s", help="sunset/sunrise",                             dest="about_sun",                    action="store_true")

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument( "-a", help="show current condition and forecast", dest="all",                          action="store_true")
    group.add_argument( "-c", help="show current condition only",         dest="current_only",                 action="store_true")
    group.add_argument( "-d", help="show forecast only",                  dest="feature_only", metavar="DAYS", type=int,            const=5, nargs="?", default=None)

    ns = parser.parse_args(namespace=ns)

    # check arguments
    if (ns.location == None):
        parser.error("Must specific location")
    if (ns.all == False and ns.current_only == False and ns.feature_only == None and ns.about_sun == False):
        parser.error("Must specfic one type of information")

    # fix options
    if (ns.all == True):
        ns.current_only = True
        ns.feature_only = 5

    return ns

def find_woeid(location):
    yql = 'select woeid from geo.places where text="{}" limit 1'.format(location)
    url = "https://query.yahooapis.com/v1/public/yql?" + urlencode({'q': yql, 'format': 'json'})
    data = json.loads(urlopen(url).read().decode())["query"]
    if data["results"] == None:
        return None
    return int(data["results"]["place"]["woeid"])

def search_weather(location, days, unit, current = False, forecast = False, sun = False):
    woeid = find_woeid(location)
    if woeid == None:
        return ["No place on the earth called '{}'.".format(location)]

    yql = 'select * from weather.forecast where woeid="{}" and u="{}"'.format(woeid, unit)
    url = "https://query.yahooapis.com/v1/public/yql?" + urlencode({'q': yql, 'format': 'json'})
    data = json.loads(urlopen(url).read().decode())["query"]["results"]["channel"]
    unit = data["units"]["temperature"]

    result = []
    if current == True:
        result.append("{}, {}, {}{}".format(data["location"]["city"], data["item"]["condition"]["text"], data["item"]["condition"]["temp"], unit))
    if forecast == True:
        day = 0
        for item in data["item"]["forecast"]:
            if day >= days:
                break
            result.append("{} {} {}~{}{} {}".format(item["date"], item["day"], item["low"], item["high"], unit, item["text"]))
            day += 1
    if sun == True:
        result.append("sunrise: {}, sunset: {}".format(data["astronomy"]["sunrise"], data["astronomy"]["sunset"]))

    return result

def main():
    args = parse_argumnets()
    result = search_weather(args.location, args.feature_only, args.unit, args.current_only, args.feature_only != None, args.about_sun)
    print("\n".join(result))

if __name__ == '__main__':
    main()
