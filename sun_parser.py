# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 13:31:45 2020

@author: Jonat
"""

import os
import numpy as np
import pandas as pd

class SunParser(object):
    def __init__(self):

        self.name = "sun"
        self.file_name = 'sun.csv'
        self.file_path = os.path.join("data",self.file_name)
        self.label_col = "output"
        self.metric = "r2"
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

        data_cleaned = data.dropna()
        X, y = data_cleaned.drop(columns=[self.label_col]), data_cleaned[self.label_col]

        return X, y

    def _print_stats(self):
        print("#"*30 + " Start Dataset - " + self.name + " Stats " + "#"*30)
        print("Dataset shape:", self.all.shape)
        print("Counts for each class:")
        print(self.y.value_counts())
        print("Sample of first 5 rows:")
        print(self.all.head(5))
        print("#"*30 + " End Dataset Stats " + "#"*30)


if __name__ == '__main__':
    parser = SunParser()
    X, y = parser.X, parser.y