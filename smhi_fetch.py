
# -*- coding: utf-8 -*-
import requests
from sklearn.metrics.pairwise import haversine_distances
from math import radians
import requests
import json
import time
import csv
from datetime import datetime

# Default parameters to use
PARAMETERS = {
        #"sun_hours_id":10
        "air_temperature_id":1,
        "air_humidity_id":6,
        "precipitation_id":7,
        "cloud_coverage_id":16,
        "air_pressure_id":9
}


def return_nearest_station(pv_cords, parameter_ids):
    """fetches data from api.
    
    pv_cords -- A latitude and longitude coordinate (ex: [54.22,11.34])
    paramter_type -- The typ of parameter (ex: "16")    
    """
    station_ids = []
    for parameter_id in parameter_ids:
        url = "https://opendata-download-metobs.smhi.se/api/version/latest/parameter/" + str(parameter_id) + ".json"
        data = requests.get(url)
        data = data.json()
        station_id = nearest_station_id(pv_cords, data['station'])
        station_ids.append(station_id)
    return station_ids

#with open('parameter1.json') as f:
#  data2 = json.load(f)


def distance_to_station(my_cords, station_cords):    
    """Calculates distance from one coordinate to another.

    """
    my_cords_in_radians = [radians(_) for _ in my_cords]
    station_cords_in_radians = [radians(_) for _ in station_cords]
    result = haversine_distances([my_cords_in_radians, station_cords_in_radians])
    result = result * 6371000/1000  # multiply by Earth radius to get kilometers
    return result[1][0]


def nearest_station_id(my_cords, stations):
    """Returns the station with the smallest distance to chosen coordinate.
    
    """
    smallest_distance = float('inf') #max value for float
    for station in stations:
        dist = distance_to_station(my_cords,[station['latitude'], station['longitude']])
        if dist < smallest_distance:
            smallest_distance = dist
            smallest_distance_id = station['id']
            station_coordinates = [station['latitude'], station["longitude"]]
    #print(smallest_distance)
    return smallest_distance_id

#--------------------------------------------------------------
#--------------------------------------------------------------
#--------------------------------------------------------------

def fetch_smhi_parameter(parameter_id, station_id, period, version):
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
    #json_formatted_str = json.dumps(json_data, indent=2)
    #print(json_formatted_str)
    return json_data

def fetch_smhi_parameters(station_ids, parameters, period="latest-day", version="latest"):
    """Makes API call to retrieve multiple parameters.


    Keyword arguments:
    station_ids -- list of SMHI ids of stations to retrieve from
    period -- time frame of retrieval
    version -- version of SMHI API
    parameters -- parameters to retrieve
    """

    parameter_dicts = {}
    for station_id, parameter in zip(station_ids, parameters.keys()):
        parameter_data = fetch_smhi_parameter(parameters[parameter],
                                              station_id, period, version)
        save_json(parameter_data, parameter)
        #parameter_data = read_json(parameter)
        #print(parameter_data["value"])
        data_points = parameter_data["value"]
        parameter_dict = {}
        if data_points is not None:
            for data_point in data_points:
                parameter_dict[data_point["date"]] = data_point["value"]
            parameter_dicts[parameter] = parameter_dict
    return parameter_dicts

def get_strong_data(start_date, end_date, latitude, longitude):
    start_date = datetime.fromtimestamp(start_date/1000)
    end_date = datetime.fromtimestamp(end_date/1000)
    #print("enddate: " + str(end_date))
    
    url = 'http://strang.smhi.se/extraction/getseries.php?par=116&m1='+ str(start_date.month) +'&d1='+ str(start_date.day) +'&y1='+ str(start_date.year) + \
     '&h1=' + str(start_date.hour) +'&m2='+ str(end_date.month) +'&d2='+ str(end_date.day) +'&y2='+ str(end_date.year) +'&h2=' + str(end_date.hour) + '&lat='+ str(latitude) +'&lon='+ str(longitude) +'&lev=0'
     
    data = requests.get(url)
    #print(data.text)
    lines = data.text.splitlines()
    print(lines)
    sunhours = []
    for line in lines:
        date = line.split()
        year = int(date[0])
        month = int(date[1])
        day = int(date[2])
        hour = int(date[3])
        d = datetime(year,month,day,hour).timestamp()
        print(datetime.fromtimestamp(d))
        sunhours.append(date[4])
        
    return sunhours

def save_smhi_parameters_to_csv(parameter_dicts, latitude, longitude):
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
        
        
    # write to csv
    file_handle = open('smhi.csv', 'w', newline='')
    with file_handle:
        writer = csv.writer(file_handle)
        titles = ["date"]
        for parameter in parameter_dicts.keys():
            titles.append(parameter)
        writer.writerow(titles)
        for date in dates:
           # date_t = datetime.utcfromtimestamp(date/1000)
            #print(date_t)
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
    
    strong_data = get_strong_data(min(dates), max(dates), latitude, longitude)
    print(strong_data)
    

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

def get_smhi_data_from_stations(station_ids, parameters):
    """Fetches SMHI data and stores it using csv-format

    Keyword arguments:
    station_id -- id of station to retrieve from
    """

    data = fetch_smhi_parameters(station_ids, parameters)
    return data

def get_smhi_data_from_coordinates(latitude, longitude, parameters=PARAMETERS):
    station_ids = return_nearest_station([latitude, longitude], parameters.values())
    data = get_smhi_data_from_stations(station_ids, parameters)
    return data

if __name__ == "__main__":
    longitude = 16.862620
    latitude = 59.938480
    data = get_smhi_data_from_coordinates(latitude, longitude)
    save_smhi_parameters_to_csv(data, latitude, longitude)