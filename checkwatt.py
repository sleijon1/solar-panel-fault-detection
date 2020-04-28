import csv
from datetime import datetime, timezone


def create_files():
    with open('checkwatt_metadata.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            if len(row['Id']) == 18:
                file_name = row['Id']
                file_handle = open("data/" + str(file_name) + ".csv", 'w')


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

    path = building_id + ".csv"
    new_path = building_id + "_new.csv"

    try:
        with open(path, "r") as read_obj:
            reader = csv.DictReader(read_obj)

            output = []
            for row in reader:
                date = int(row["date"])
                smhi_col1.append(date)
                smhi_col2.append(row["air_temperature_id"])
                smhi_col3.append(row["air_humidity_id"])
                smhi_col4.append(row["precipitation_id"])
                smhi_col5.append(row["cloud_coverage_id"])
                smhi_col6.append(row["air_pressure_id"])

                try:
                    value = building_data[date]
                    output.append(value)
                except KeyError:
                    output.append(None)
                    if verbose:
                        print("KeyError: " + str(date) + " for id: " + building_id + ".")           

        
        with open(new_path, "w", newline='') as write_obj:
            fieldnames =  ["date", "air_temperature_id", "air_humidity_id", \
                "precipitation_id", "cloud_coverage_id", "air_pressure_id", "output"]
            writer = csv.writer(write_obj)
            writer.writerow(fieldnames)
            rows = zip(smhi_col1, smhi_col2, smhi_col3, smhi_col4, smhi_col5, \
                    smhi_col6, output)
            for row in rows:
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

    print("###########################")
    print("# Building_ids found: " + str(csvs_written+csvs_not_found) + "  #")
    print("# Csv files written to: " + str(csvs_written) + " #")
    print("# Missing csv files: " + str(csvs_not_found) + "   #")
    print("###########################")

if __name__ == "__main__":
    checkwatt(verbose=True)
    

