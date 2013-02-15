#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
from contextlib import closing
from lxml.etree import parse as parse_xml

from melange import api


CURRENT_URL = 'http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?query={0}'
FORECAST_URL = 'http://api.wunderground.com/auto/wui/geo/ForecastXML/index.xml?query={0}'
KILOMETER_MILES_RATIO = 1.609

@api.register('org.cream.melange.WeatherWidget')
class Weather(api.API):

    @api.expose
    def get(self):
        # Loading current weather data…
        current_url = CURRENT_URL.format(self.config.location)
        with closing(urllib.urlopen(current_url)) as file_handle:
            current_data = parse_xml(file_handle)

        # Loading forecast data…
        forecast_url = FORECAST_URL.format(self.config.location)
        with closing(urllib.urlopen(forecast_url)) as file_handle:
            forecast_data = parse_xml(file_handle)

        forecast = []

        for day in forecast_data.find('simpleforecast').getchildren()[1:4]:
            forecast.append(day.find('icon').text)

        return {
            'current': {
                'weather': current_data.find('weather').text,
                'temperature': current_data.find('temp_c').text,
                'humidity': current_data.find('relative_humidity').text[:-1], # strip the '%'
                'wind_direction': current_data.find('wind_dir').text,
                'wind_speed': str(round(float(current_data.find('wind_mph').text) * KILOMETER_MILES_RATIO, 1)),
                'pressure': current_data.find('pressure_mb').text,
                'visibility': current_data.find('visibility_km').text,
                'icon': current_data.find('icon').text
            },
            'forecast': forecast
        }
