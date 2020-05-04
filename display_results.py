# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 17:03:46 2020

@author: Jonat
"""

import numpy as np
import operator
import os
import pandas as pd
file_name = "sun_score.csv"
results_file = os.path.join("data",file_name)
results_df = pd.read_csv(results_file).dropna().round(3)

temp = results_df.copy()
temp["model"] = results_df["Classifier_Name"].apply(lambda sen: sen.split("_")[1])
temp["scaler"] = results_df["Classifier_Name"].apply(lambda sen: sen.split("_")[0])

pivot_t_RMSE = pd.pivot_table(temp, values='RMSE', index=["scaler"], columns=['model'], aggfunc=np.sum)
pivot_t_R2 = pd.pivot_table(temp, values='R2_score', index=["scaler"], columns=['model'], aggfunc=np.sum)
print(pivot_t_RMSE)
print(pivot_t_R2)