import requests
import json



def fetch_smhi_parameter(parameter_id, station_id, period, version):
    base_url = r"https://opendata-download-metobs.smhi.se/"
    api_call = r"api/version/"+version+"/parameter/"+parameter_id+"/station/"+station_id+"/period/"+period+"/data.json"
    url = base_url + api_call
    response = requests.get(url)
    json_data =  json.loads(response.text)
    print(json.dumps(json_data, sort_keys=True, indent=4))
    
    return json_data

def fetch_smhi_parameters(station_id, period="latest-months", version="latest"):
    parameters = {
        #"sun_hours_id":10
        #"air_temperature_id":1,
        #"air_humidity_id":6,
        #"precipitation_id":7,
        #"cloud_coverage_id":16,
        "air_pressure_id":9
    }
    for parameter_id in parameters.values():
        parameter_data = fetch_smhi_parameter(str(parameter_id), station_id, period, version)
        
        
def test_json():
    with open('data.txt', 'r') as readfile:
        json_data = json.load(readfile)

    print(json_data)
    print(len(json_data["value"]))

test_json()
#fetch_smhi_parameters("159880")
