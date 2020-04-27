import csv
from datetime import datetime, timezone


def create_files():
    with open('checkwatt_metadata.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            if len(row['Id']) == 18:
                file_name = row['Id']
                file_handle = open("data/" + str(file_name) + ".csv", 'w')


def find_pointer(timestamp, reader):
    row_count = sum(1 for row in reader)
    for i in range(1, row_count):
        row = next(reader)
        if row[0] == timestamp:
            return row, reader
        
    return None
                
def read_checkwatt_data():
    with open('checkwatt_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        row_count = 0
        current_id = None
        read_obj = None
        write_obj = None
        j = 0
        for cw_row in reader:
            date = cw_row[2]
            date = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
            #TODO not *1000 XD
            date_utctimestamp = int(date.replace(tzinfo=timezone.utc).timestamp())*1000
            building_id = cw_row[0]

            try:
                if current_id != building_id:
                    current_id = building_id

                    if read_obj is not None:
                        read_obj.close()
                    if write_obj is not None:
                        write_obj.close()
                        
                    read_obj = open("data/" + str(current_id) + ".csv", 'r')
                    write_obj = open("data/" + str(current_id) + "_new.csv", 'w', newline='')
                    read_obj.readline()
                    #csv_reader = csv.reader(read_obj)
                    #csv_writer = csv.writer(write_obj)

                    #first_row = next(csv_reader)
                    #first_row.append("output")
                    #csv_writer.writerow(first_row)
                    print(date_utctimestamp)
                values = []
                for index in range(10, 58, 2):
                    values.append(float(cw_row[index].replace(',', '.')))
                    my_bool = False
                    i = 0
                print(read_obj)
                for smhi_row in read_obj:
                    smhi_row = smhi_row.split(',')
                    j += 1 
                    if int(smhi_row[0]) == date_utctimestamp:
                        print("True")
                        print(values)
                        print(date_utctimestamp)
                        my_bool = True
                    if my_bool:
                        smhi_row.append(values[i])
                        i+=1
                        if i == 24:
                            my_bool = False
                            #csv_writer.writerow(smhi_row)
                            write_obj.writelines(smhi_row)
                            row_count += 1
            except:
                #print("Could not write to: " + str(file_name))
                pass
        print(j)
        if read_obj is not None:
            read_obj.close()
        if write_obj is not None:
                write_obj.close()
                        

if __name__ == "__main__":
    #create_files()
    read_checkwatt_data()
