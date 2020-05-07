import csv
from datetime import datetime, timezone
import smhi_fetch
import pgeocode
import numpy as np
import os

def find_building_ids():
    """ Returns all building ids from hpsolartech_data.csv
    
    """
    ids = []
    with open('data/hpsolartech_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            if row[0] not in ids:
                ids.append(row[0])
    return ids


def find_first_year(wanted_id):
    """ Returns the first year for which data exists for a given building id

	Keyword arguments
	wanted_id -- id of the wanted building
    """
    oldest_date = 3000
    with open('data/hpsolartech_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            building_id = row[0]
            if building_id == wanted_id:
                date = row[2]
                formatted_date = int(date[:4])
                if formatted_date < oldest_date:
                    oldest_date = formatted_date
    return str(oldest_date)

def print_good_building_ids():
    """ Reads hpsolartech_metadata.csv and creates .csv files containing smhi data
    for every building with available zip-code/(lat,long)-coords.

    """
    initials = ["JK", "SL", "PS", "HW"]
    avail_ids = find_building_ids()
    building_count = 0
    with open('data/hpsolartech_metadata.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        skipped_buildings = 0
        for row in reader:
            if len(row['Id']) == 18 and row['Id'] in avail_ids: 
                building_id = row['Id']
                latitude = row['Latitude']
                longitude = row['Longitude']
                zip_code =  row['ZipCode']

                if zip_code == "0" and latitude == "null" and longitude == "null":
                    print("No geographical data, skipping " + building_id)
                    skipped_buildings += 1
                    continue
                
                if latitude == "null" or longitude == "null":
                    # get lat, long from zip code
                    zip_code = zip_code[:3] + ' ' + zip_code[3:]
                    nomi = pgeocode.Nominatim('se')
                    df = nomi.query_postal_code(zip_code)
                    latitude = df['latitude']
                    longitude = df['longitude']
                    if np.isnan(latitude) or np.isnan(longitude):
                        print("Couldn't retrieve lat,long from zip code for building " + building_id)
                        skipped_buildings += 1
                        continue

                building_count += 1
                print(str(building_count) + ": (" + initials[building_count%4] + ")" + " building_id: " + str(building_id))

def create_building_files():
    """ Reads hpsolartech_metadata.csv and creates .csv files containing smhi data
    for every building with available zip-code/(lat,long)-coords.

    """
    avail_ids = find_building_ids()
    building_count = 0
    with open('data/hpsolartech_metadata.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        skipped_buildings = 0
        for row in reader:
            if len(row['Id']) == 18 and row['Id'] in avail_ids: 
                building_id = row['Id']
                latitude = row['Latitude']
                longitude = row['Longitude']
                zip_code =  row['ZipCode']

                if zip_code == "0" and latitude == "null" and longitude == "null":
                    print("No geographical data, skipping " + building_id)
                    skipped_buildings += 1
                    continue
                
                if latitude == "null" or longitude == "null":
                    # get lat, long from zip code
                    zip_code = zip_code[:3] + ' ' + zip_code[3:]
                    nomi = pgeocode.Nominatim('se')
                    df = nomi.query_postal_code(zip_code)
                    latitude = df['latitude']
                    longitude = df['longitude']
                    if np.isnan(latitude) or np.isnan(longitude):
                        print("Couldn't retrieve lat,long from zip code for building " + building_id)
                        skipped_buildings += 1
                        continue

                print("Building_id: " + str(building_id))
                latitude = float(latitude)
                longitude = float(longitude)
                data = smhi_fetch.get_smhi_data_from_coordinates(latitude, longitude, "corrected-archive", find_first_year(building_id))
                path = "data/buildings/" + building_id + ".csv"
                status_code = smhi_fetch.save_smhi_parameters_to_csv(data, latitude, longitude, path)
                if status_code == 1:
                    building_count += 1
                    print("Building done: " + building_id + ", Total buildings done: " \
                      + str(building_count))
                    print("------------------------------------------------------------")
                elif status_code == 0:
                    print("'save_smhi_parameters_to_csv' was given an empty parameter_dict")
                if building_count ==3:
                    return
        print("Couldn't find building_id: " + wanted_id)
def read_hpsolartech_data():
    """ Returns values of power output for all buildings contained in 
    hpsolartech_data.csv as a dictionary

    """
    with open('data/hpsolartech_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        hpsolartech_dict = {}
        previous_building_id = None
        building_dict = {}
        for cw_row in reader:
            building_id = cw_row[0]
            if building_id != previous_building_id:
                building_dict = {}
            date = cw_row[2]
            date = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
            #TODO not *1000 XD
            date_utctimestamp = int(date.replace(tzinfo=timezone.utc).timestamp())*1000
        
            if len(cw_row) != 58:
                # Data read badly, skip
                continue

            values = []
            timestamps = []
            for index in range(0, 24, 1):
                # TODO remove *1000 on timestamp
                values.append(float(cw_row[2*index+10].replace(',', '.')))
                timestamps.append(date_utctimestamp + index*3600*1000)

            for timestamp, value in zip(timestamps, values):
                building_dict[timestamp] = value

            hpsolartech_dict[previous_building_id] = building_dict
            previous_building_id = building_id
    del hpsolartech_dict[None]
    return hpsolartech_dict


def write_hpsolartech_data(building_id, building_data, verbose):
    """ writes building data to a .csv file
    
    building_id -- id of building
    building_data -- dictionary mapping timestamps to values
    verbose -- bool for more information

    """
    path = "data/buildings/" + building_id + ".csv"
    new_path = "data/buildings/" + building_id + "_new.csv"

    try:
        with open(path, "r") as read_obj:
            reader = csv.DictReader(read_obj)
            fieldnames = reader.fieldnames

            data_dict = {}
            output = []
            for fieldname in fieldnames:
                data_dict[fieldname] = []

            for row in reader:
                date = int(row["date"])

                for fieldname in fieldnames:
                    data_dict[fieldname].append(row[fieldname])

                try:
                    value = building_data[date]
                    output.append(value)
                except KeyError:
                    output.append(None)
                    if verbose:
                        print("KeyError: " + str(date) + " for id: " + building_id + ".")
        with open(new_path, "w", newline='') as write_obj:
            data_dict['output'] = output
            fieldnames.append("output")
            writer = csv.writer(write_obj)
            writer.writerow(fieldnames)


            length = len(data_dict[fieldnames[0]])
            for i in range(0, length):
                row = []
                for fieldname in fieldnames:
                    row.append(data_dict[fieldname][i])
                writer.writerow(row)



        if verbose:
            print("File " + path + " done.")
        os.remove(path)
        os.rename(new_path, path)
        return True
    except FileNotFoundError:
        if verbose:
            print("No .csv file found for " + building_id + ".")
        return False


def fill_hpsolartech_files(verbose=False):
    """Fills all .csv files with power output column from hpsolartech_data.csv file
    
    verbose -- bool for more information
    """
    hpsolartech_data = read_hpsolartech_data()
    csvs_written = 0
    csvs_not_found = 0
    for building_id in hpsolartech_data.keys():
        wrote = write_hpsolartech_data(building_id, hpsolartech_data[building_id], verbose)
        if wrote:
            csvs_written += 1
        else:
            csvs_not_found += 1


    longest_line = "# Csv files written to: " + str(csvs_written) + " #"
    length = len(longest_line)

    print("")
    print(length*"#")
    print("# Building_ids found: " + str(csvs_written+csvs_not_found) + (length-(len(str(csvs_written+csvs_not_found))+23))*" " +  "#")
    print("# Csv files written to: " + str(csvs_written) + " #")
    print("# Missing csv files: " + str(csvs_not_found) + (length-(len(str(csvs_not_found))+22))*" " +  "#")
    print(length*"#")

if __name__ == "__main__":
    #print_good_building_ids()
    
    #input_id = str(input("Type in building id, if unsure use function: print_good_building_ids()\nbuilding_id: "))
    try:
        create_building_files()
    except Exception as e:
        print("create_building_files crashed. " + str(type(e).__name__) + ": " + str(e))
    fill_hpsolartech_files(verbose=False)
