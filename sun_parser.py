# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 13:31:45 2020

@author: Jonat
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timezone

class SunParser(object):
    def __init__(self):

        self.name = "sun"
        self.file_name = 'sun.csv'
        self.file_path = os.path.join("data",self.file_name)
        self.label_col = "output"
        self.metric = "neg_root_mean_squared_error"
        self.X, self.y = self._parse_file()
        self.all = pd.concat([self.X, self.y], axis=1)
        self._print_stats()

    def _parse_file(self,):
        """
            -Read csv data
            -Drop nan values
            -Keep only numeric columns
            -Split to X for features and y for labels
        """
        data = pd.read_csv(self.file_path)
        data = data.dropna()
        data["date_temp"] = data["date"].divide(1000)
        data["date_real"] = data["date_temp"].map(datetime.utcfromtimestamp)
        data["hour"] = data["date_real"].map(lambda x: x.hour)
        data["month"] = data["date_real"].map(lambda x: x.month)
        data['hr_sin'] = np.sin(data.hour*(2.*np.pi/24))
        data['hr_cos'] = np.cos(data.hour*(2.*np.pi/24))
        data['mnth_sin'] = np.sin((data.month-1)*(2.*np.pi/12))
        data['mnth_cos'] = np.cos((data.month-1)*(2.*np.pi/12))
        data.drop(columns=["date_real", "hour", "month", "date_temp"], axis=1, inplace=True)
           
        data_cleaned = data.dropna()
        
        data_cleaned["prev_output"] = data_cleaned["output"].shift(1)
        data_cleaned = data_cleaned.dropna()
        #data_cleaned = data_cleaned.drop(["air_temperature_id"], axis=1)
        for row in data_cleaned["date"]:
            if ((datetime.utcfromtimestamp(row/1000)).year < 2018) or ((datetime.utcfromtimestamp(row/1000)).month > 11) or ((datetime.utcfromtimestamp(row/1000)).month < 3):  
                indexNames = (data_cleaned[data_cleaned['date'] == row ].index)
                #print("removed: " + str(datetime.utcfromtimestamp(row/1000)))
                data_cleaned.drop(indexNames , inplace=True)


        X, y = data_cleaned.drop(columns=[self.label_col]), data_cleaned[self.label_col]

       
        return X, y

    def _print_stats(self):
        print("#"*30 + " Start Dataset - " + self.name + " Stats " + "#"*30)
        print("Dataset shape:", self.all.shape)
        print("Counts for each class:")
        print(self.y.value_counts())
        print("Sample of first 5 rows:")
        print(self.all.head(50))
        print("#"*30 + " End Dataset Stats " + "#"*30)


if __name__ == '__main__':
    parser = SunParser()
    X, y = parser.X, parser.y