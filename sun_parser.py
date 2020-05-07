# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 13:31:45 2020

@author: Jonat
"""

import numpy as np
import pandas as pd
from datetime import datetime

"Parts of the code is taken from https://github.com/shaygeller/Normalization_vs_Standardization by Shay Geller"

class SunParser(object):
    def __init__(self, file_name):
        self.file_path = file_name
        self.label_col = "output"
        self.metric = "r2"
        self.X, self.y = self._parse_file()
        self.all = pd.concat([self.X, self.y], axis=1)

    def _parse_file(self,):
        """
            -Read csv data
            -Drop nan values
            -Parameters for time series is created (sliding window and cyclical features)
            -Split to X for features and y for labels
        """
        data = pd.read_csv(self.file_path)
        data = data.dropna()
        data["date_temp"] = data["date"].divide(1000)
        data["date_real"] = data["date_temp"].map(datetime.utcfromtimestamp)
        data["hour"] = data["date_real"].map(lambda x: x.hour)
        data["month"] = data["date_real"].map(lambda x: x.month)
        
        #Cyclical features hours and months represented as parameters
        data['hr_sin'] = np.sin(data.hour*(2.*np.pi/24))
        data['hr_cos'] = np.cos(data.hour*(2.*np.pi/24))
        data['mnth_sin'] = np.sin((data.month-1)*(2.*np.pi/12))
        data['mnth_cos'] = np.cos((data.month-1)*(2.*np.pi/12))
        
        #Drop temporary columns
        data.drop(columns=["date_real", "hour", "month", "date_temp"], axis=1, inplace=True)
          
        data = data.dropna()
        
        #Sliding window 
        for i in range(1,5):    
            data["prev_output_" + str(i)] = data["output"].shift(i)       
        
        #removes rows in the beginning and end that was created after the sliding window    
        data = data.dropna()
        X, y = data.drop(columns=[self.label_col]), data[self.label_col]
       
        return X, y

    def _print_stats(self):
        """
            Prints stats about the dataset
        """
        print("#"*30 + " Start Dataset - " + " Stats " + "#"*30)
        print("Dataset shape:", self.all.shape)
        print("Counts for each class:")
        print(self.y.value_counts())
        print("Sample of first 5 rows:")
        print(self.all.head(5))
        print("#"*30 + " End Dataset Stats " + "#"*30)

