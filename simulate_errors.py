import pandas as pd
import os

def simulate_decrease(decrease_list, y_test):
   decreased_output = y_test.values.tolist()
   y_len = len(y_test)
   for decrease_info in decrease_list:
       start_index = round(decrease_info[0] * y_len)
       end_index = round(decrease_info[1] * y_len)
       for i in range(start_index, end_index):

           decreased_output[i] = decreased_output[i] * decrease_info[2] 

   return decreased_output

if __name__ == '__main__':
    print("Invoking simulating_errors as main wtf")
