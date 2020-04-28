import csv
from datetime import datetime, timezone
import smhi_fetch
import pgeocode
import numpy as np


def create_files():
    with open('checkwatt_metadata.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        skipped_buildings = 0
        for row in reader:
            if len(row['Id']) == 18:
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

                latitude = float(latitude)
                longitude = float(longitude)
                data = smhi_fetch.get_smhi_data_from_coordinates(latitude, longitude, "latest-months")
                path = "data/" + building_id + ".csv"
                smhi_fetch.save_smhi_parameters_to_csv(data, latitude, longitude, path)
                print("Building done: " + building_id)

def read_checkwatt_data():
    with open('checkwatt_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        checkwatt_dict = {}
        previous_building_id = None
        building_dict = {}
        for cw_row in reader:
            building_id = cw_row[0]
            if building_id != previous_building_id:
                checkwatt_dict[previous_building_id] = building_dict
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
            previous_building_id = building_id
    del checkwatt_dict[None]
    return checkwatt_dict


def write_checkwatt_data(building_id, building_data, verbose):
    """
    writes building data to a .csv file

    """

    smhi_col1 = []
    smhi_col2 = []
    smhi_col3 = []
    smhi_col4 = []
    smhi_col5 = []
    smhi_col6 = []

    

    path = "data/" + building_id + ".csv"
    new_path = "data/" + building_id + "_new.csv"

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
        return True
    except FileNotFoundError:
        if verbose:
            print("No .csv file found for " + building_id + ".")
        return False


def checkwatt(verbose=False):
    checkwatt_data = read_checkwatt_data()
    csvs_written = 0
    csvs_not_found = 0
    for building_id in checkwatt_data.keys():
        wrote = write_checkwatt_data(building_id, checkwatt_data[building_id], verbose)
        if wrote:
            csvs_written += 1
        else:
            csvs_not_found += 1

    longest_line = "# Csv files written to: " + str(csvs_written) + " #"
    length = len(longest_line)

    print(length*"#")
    print("# Building_ids found: " + str(csvs_written+csvs_not_found) + (length-(len(str(csvs_written+csvs_not_found))+23))*" " +  "#")
    print("# Csv files written to: " + str(csvs_written) + " #")
    print("# Missing csv files: " + str(csvs_not_found) + (length-(len(str(csvs_not_found))+22))*" " +  "#")
    print(length*"#")

if __name__ == "__main__":
    try:
        create_files()
    except:
        print("SMHI_FETCH CRASHING")
    checkwatt(verbose=False)
