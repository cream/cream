#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
from contextlib import closing
from lxml.etree import parse as parse_xml

from cream.contrib.melange import api


WEATHER_REQUEST_URL = 'http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?query={0}'
KILOMETER_MILES_RATIO = 1.609


@api.register('weather')
class Weather(api.API):

    @api.expose
    def get(self, location):
        url = WEATHER_REQUEST_URL.format(location)
        with closing(urllib.urlopen(url)) as file_handle:
            weather_data = parse_xml(file_handle)

        return {
            'weather': weather_data.find('weather').text,
            'temperature': weather_data.find('temp_c').text,
            'humidity': weather_data.find('relative_humidity').text[:-1], # strip the '%'
            'wind_direction': weather_data.find('wind_dir').text,
            'wind_speed': str(round(float(weather_data.find('wind_mph').text) * KILOMETER_MILES_RATIO, 1)),
            'pressure': weather_data.find('pressure_mb').text,
            'visibility': weather_data.find('visibility_km').text,
            'icon': weather_data.find('icon').text
            }
