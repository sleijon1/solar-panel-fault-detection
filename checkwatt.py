import csv


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
        for row in reader:
            file_name = row[0]
            try:
                with open("data/" + str(file_name) + ".csv", 'r') as read_obj, \
                     open("data/" + str(file_name) + "_new.csv", 'w', newline='') as write_obj:
                    csv_reader = csv.reader(read_obj)
                    csv_writer = csv.writer(write_obj)
                    for row in csv_reader:
                        if row[0] == "date":
                            row.append("output")
                        else:
                            row.append("xd")
                        csv_writer.writerow(row)
            except:
                print("Could not write to: " + str(file_name))

if __name__ == "__main__":
    #create_files()
    read_checkwatt_data()
