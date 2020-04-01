import requests
import json
import csv

PARAMETERS = {
        #"sun_hours_id":10
        "air_temperature_id":1,
        "air_humidity_id":6,
        "precipitation_id":7,
        "cloud_coverage_id":16,
        "air_pressure_id":9
    }

def fetch_smhi_parameter(parameter_id, station_id, period, version):
    base_url = r"https://opendata-download-metobs.smhi.se/"
    api_call = r"api/version/"+version+"/parameter/"+parameter_id+"/station/"+station_id+"/period/"+period+"/data.json"
    url = base_url + api_call
    response = requests.get(url)
    json_data =  json.loads(response.text)
    
    return json_data

def fetch_smhi_parameters(station_id, period="latest-months", version="latest", parameters=PARAMETERS):
    parameter_dicts = {}
    for parameter in parameters.keys():
        #parameter_data = fetch_smhi_parameter(str(parameters[parameter]), station_id, period, version)
        #save_json(parameter_data, parameter)
        parameter_data = read_json(parameter)
        data_points = parameter_data["value"]
        parameter_dict = {}
        for data_point in data_points:
            parameter_dict[data_point["date"]] = data_point["value"]
        parameter_dicts[parameter] = parameter_dict 
    return parameter_dicts

def save_smhi_parameters_to_csv(parameter_dicts):
    # Get all unixtimestamps (dates)
    dates = []
    for parameter in parameter_dicts:
        parameter_dict = parameter_dicts[parameter]

        for date in parameter_dict.keys():
            if date not in dates:
                dates.append(date)

    # write to csv
    file_handle = open('smhi.csv', 'w', newline='')
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

def save_json(data, filename):
    with open(filename+".txt", 'w') as outfile:
        json.dump(data, outfile)
        
def read_json(filename, extension=".txt"):
    with open(filename+extension, 'r') as readfile:
        json_data = json.load(readfile)
    return json_data

def get_smhi_data_from_station(station_id):
    data = fetch_smhi_parameters(station_id)
    save_smhi_parameters_to_csv(data)

get_smhi_data_from_station("159880")