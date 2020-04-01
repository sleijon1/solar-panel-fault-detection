# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 12:50:21 2020

@author: Jonat
"""

import requests
import json
import sklearn
from sklearn.metrics.pairwise import haversine_distances
from math import radians

clouds = "16"
air_temperature = "1"
global_irradiance = "10"
precipitation = "7"
air_pressure = "9"
humidity = "6"
bunkern = [59.873511,17.625153]


def return_nearest_station(pv_cords, parameter_type):
    url = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/" + parameter_type + ".json"
    data = requests.get(url)
    data = data.json()
    return nearest_station_id(pv_cords, data['station'])

with open('parameter1.json') as f:
  data2 = json.load(f)

def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def distance_to_station(my_cords, station_cords):    
    my_cords_in_radians = [radians(_) for _ in my_cords]
    station_cords_in_radians = [radians(_) for _ in station_cords]
    result = haversine_distances([my_cords_in_radians, station_cords_in_radians])
    result = result * 6371000/1000  # multiply by Earth radius to get kilometers
    return result[1][0]

def nearest_station_id(my_cords, stations):
    smallest_distance = float('inf')
    print(len(stations))
    for station in stations:
        dist = distance_to_station(my_cords,[station['latitude'], station['longitude']])
        if dist < smallest_distance:
            smallest_distance = dist
            smallest_distance_id = station['id']
    return  smallest_distance_id

print(return_nearest_station(bunkern, global_irradiance))
