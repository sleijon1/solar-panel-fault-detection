# -*- coding: utf-8 -*-
import requests
from sklearn.metrics.pairwise import haversine_distances
from math import radians
import requests
import json
import time
import csv
from datetime import datetime,timezone
import pandas as pd 
from contextlib import closing
import codecs

# Default parameters to use
PARAMETERS = {
        #sun_hours_weak_id":10,
        "air_temperature_id":1,
        "air_humidity_id":6,
        "precipitation_id":7,
        "cloud_coverage_id":16,
        "air_pressure_id":9
}

# Smhi periods
PERIODS = {
    "latest-hour":0,
    "latest-day":1,
    "latest-months":2,
    "corrected-archive":3
}

def return_nearest_station(pv_cords, parameter_ids, period):
    """fetches data from api.
    
    pv_cords -- A latitude and longitude coordinate (ex: [54.22,11.34])
    paramter_type -- The typ of parameter (ex: "16")
    period -- time frame of retrieval
    """
    station_ids = []
    for parameter_id in parameter_ids:
        url = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/" + \
            str(parameter_id) + ".json"
        data = requests.get(url)
        data = data.json()
        station_id = nearest_station_id(pv_cords, data['station'], period)
        station_ids.append(station_id)
    return station_ids


def nearest_station_id(my_cords, stations, period):
    """Returns the station id with the smallest distance to chosen coordinate
    or None if no station has the given period.
    
    period -- time frame of retrieval
    """
    distances = []
    for station in stations:
        dist = distance_to_station(my_cords,[station['latitude'], station['longitude']])
        distances.append((station, dist))
    sorted_distances = sorted(distances, key=lambda x: x[1])
    
    smallest_distance = float('inf') #max value for float
    smallest_distance_id = None
    for station, dist in sorted_distances:
        url = station["link"][0]["href"]
        data = requests.get(url)
        data = data.json()
        available_period = data["period"][0]["key"]
        if dist > 100:
            print("Distance to nearest station above 100km. Disregarding parameter.")
            break
        if PERIODS[available_period] <= PERIODS[period]:
            smallest_distance_id = station['id']
            break

    if smallest_distance_id is None:
        print("COULD NOT FIND STATION FOR GIVEN PERIOD.")

    return smallest_distance_id


def distance_to_station(my_cords, station_cords):
    """Calculates distance from one coordinate to another.

    """
    my_cords_in_radians = [radians(_) for _ in my_cords]
    station_cords_in_radians = [radians(_) for _ in station_cords]
    result = haversine_distances([my_cords_in_radians, station_cords_in_radians])
    result = result * 6371000/1000  # multiply by Earth radius to get kilometers
    return result[1][0]

#--------------------------------------------------------------
#--------------------------------------------------------------
#--------------------------------------------------------------


def fetch_smhi_parameter_csv(station_id, parameter_id, period, version):
    """Makes API call to retrieve one parameter.


    Keyword arguments:
    parameter_id -- SMHI id of retrieved parameter
    station_id -- SMHI id of station to retrieve from
    period -- time frame of retrieval
    version -- version of SMHI API
    """
    base_url = r"https://opendata-download-metobs.smhi.se/"
    api_call = r"api/version/"+version+"/parameter/"+str(parameter_id) \
        +"/station/"+str(station_id)+"/period/"+period+"/data.csv"
    url = base_url + api_call
    response = requests.get(url)
    return(response.text)


def fetch_smhi_parameters_csv(station_ids, parameters, period, version="latest"):
    parameter_dicts = {}
    for station_id, parameter in zip(station_ids, parameters.keys()):
        parameter_data = fetch_smhi_parameter_csv(station_id, parameters[parameter], period, version)

        cutoff = parameter_data.find('2012')
        parameter_data = parameter_data[cutoff:]
        parameter_dict = {}
            
        lines = parameter_data.splitlines()
        for line in lines:
            row = line.split(';')
            
            date = row[0].split('-')
            if(date == ['']):
                continue
            year = int(date[0])
            month = int(date[1])
            day = int(date[2])
            hour = int(row[1].split(':')[0])
            value = row[2]
            d = datetime(year,month,day,hour).replace(tzinfo=timezone.utc).timestamp()
            parameter_dict[int(d) * 1000] = value
        parameter_dicts[parameter] = parameter_dict   
    return parameter_dicts    
    

def fetch_smhi_parameters_json(station_ids, parameters, period, version="latest"):
    """Makes API call to retrieve multiple parameters.


    Keyword arguments:
    station_ids -- list of SMHI ids of stations to retrieve from
    period -- time frame of retrieval
    version -- version of SMHI API
    parameters -- parameters to retrieve
    """

    parameter_dicts = {}
    for station_id, parameter in zip(station_ids, parameters.keys()):
        try:
            parameter_data = fetch_smhi_parameter_json(station_id, parameters[parameter], period, version)
            data_points = parameter_data["value"]
            parameter_dict = {}
            if data_points is not None:
                for data_point in data_points:
                    parameter_dict[data_point["date"]] = data_point["value"]
                    parameter_dicts[parameter] = parameter_dict
        except:
            print("CANT FETCH PARAMETER: " + parameter + " FROM STATION: " + str(station_id))
    return parameter_dicts

def fetch_smhi_parameter_json(station_id, parameter_id, period, version):
    """Makes API call to retrieve one parameter.


    Keyword arguments:
    parameter_id -- SMHI id of retrieved parameter
    station_id -- SMHI id of station to retrieve from
    period -- time frame of retrieval
    version -- version of SMHI API
    """
    base_url = r"https://opendata-download-metobs.smhi.se/"
    api_call = r"api/version/"+version+"/parameter/"+str(parameter_id) \
        +"/station/"+str(station_id)+"/period/"+period+"/data.json"
    url = base_url + api_call
    response = requests.get(url)
    json_data = json.loads(response.text)
    
    return json_data





def get_strong_data(start_date, end_date, latitude, longitude):
    start_date = datetime.utcfromtimestamp(start_date/1000)
    end_date = datetime.utcfromtimestamp(end_date/1000)
    
    url = 'http://strang.smhi.se/extraction/getseries.php?par=116&m1='+ str(start_date.month) +'&d1='+ str(start_date.day) +'&y1='+ str(start_date.year) + \
     '&h1=' + str(start_date.hour) +'&m2='+ str(end_date.month) +'&d2='+ str(end_date.day) +'&y2='+ str(end_date.year) +'&h2=' + str(end_date.hour) + '&lat='+ str(latitude) +'&lon='+ str(longitude) +'&lev=0'
     
    data = requests.get(url)
    lines = data.text.splitlines()
  
    sunhours = {}
    for line in lines:
        date = line.split()
        year = int(date[0])
        month = int(date[1])
        day = int(date[2])
        hour = int(date[3])
        d = datetime(year,month,day,hour).replace(tzinfo=timezone.utc).timestamp()
        sunhours[int(d) * 1000] = date[4]

        
    return sunhours

def save_smhi_parameters_to_csv(parameter_dicts, latitude, longitude, filename="smhi.csv"):
    """Saves parameters to smhi.csv


    Keyword arguments:
    parameter_dicts -- dictionary containing dictionaries of parameters
    """
    # Get all unixtimestamps (dates)
    dates = []
    remove_dates = []
    for parameter in parameter_dicts:
        parameter_dict = parameter_dicts[parameter]
        for date in parameter_dict.keys():
            if date not in dates:
                dates.append(date)

    
    for date in dates:
        date_t = datetime.utcfromtimestamp(date/1000)
        if date_t.day == datetime.utcnow().day and date_t.month == datetime.utcnow().month and date_t.year == datetime.utcnow().year:
            remove_dates.append(date)
    
    for date in remove_dates:
        dates.remove(date)
   
       
    #strong_data = get_strong_data(min(dates), max(dates), latitude, longitude)
    #parameter_dicts["sun_hours_id"] = strong_data
    
    # write to csv
    file_handle = open(filename, 'w', newline='')
    print("Writing to csv...")
    with file_handle:
        writer = csv.writer(file_handle)
        titles = ["date"]
        for parameter in parameter_dicts.keys():
            titles.append(parameter)
        writer.writerow(titles)
        for date in dates:
            row = [date]
            for parameter in parameter_dicts:
                parameter_dict = parameter_dicts[parameter]
                # If column has no value, fill with None
                try:
                    value = parameter_dict[date]
                except KeyError:
                    value = None
                    
                row.append(value)
            writer.writerow(row)
    
    

def save_json(data, filename, extension=".txt"):
    """Saves json-data in filename

    Keyword arguments:
    extension -- file extension (default: .txt)
    """

    with open(filename+extension, 'w') as outfile:
        json.dump(data, outfile)

def read_json(filename, extension=".txt"):
    """Reads json-data from filename

    Keyword arguments:
    extension -- file extension (default: .txt)
    """

    with open(filename+extension, 'r') as readfile:
        json_data = json.load(readfile)
    return json_data

def get_smhi_data_from_stations(station_ids, parameters, period):
    """Fetches SMHI data and stores it using csv-format

    Keyword arguments:
    station_id -- id of station to retrieve from
    """
    if period == "corrected-archives":
        data = fetch_smhi_parameters_csv(station_ids, parameters, period)
    else:
        data = fetch_smhi_parameters_json(station_ids, parameters, period)
    return data

def get_smhi_data_from_coordinates(latitude, longitude, period, parameters=PARAMETERS):
    station_ids = return_nearest_station([latitude, longitude], parameters.values(), period)
    data = get_smhi_data_from_stations(station_ids, parameters, period)
    return data

if __name__ == "__main__":
    latitude = 59.938480
    longitude = 16.862620
    data = get_smhi_data_from_coordinates(latitude, longitude, "latest-months")
    save_smhi_parameters_to_csv(data, latitude, longitude)
