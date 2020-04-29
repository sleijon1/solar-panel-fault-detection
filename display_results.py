# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 17:03:46 2020

@author: Jonat
"""

import numpy as np
import operator
import os
import pandas as pd
file_name = "sun_results.csv"
results_file = os.path.join("data",file_name)
results_df = pd.read_csv(results_file).dropna().round(3)

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property 'color: red' for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0.8 else 'black'
    return 'color: %s' % color

temp = results_df.copy()
temp["model"] = results_df["Classifier_Name"].apply(lambda sen: sen.split("_")[1])
temp["scaler"] = results_df["Classifier_Name"].apply(lambda sen: sen.split("_")[0])
def df_style(val):
    return 'font-weight: bold'
pivot_t = pd.pivot_table(temp, values='Test_score', index=["scaler"], columns=['model'], aggfunc=np.sum)

print(pivot_t)