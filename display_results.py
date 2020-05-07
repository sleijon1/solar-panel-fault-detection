# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 17:03:46 2020

@author: Jonat
"""
import numpy as np
import os
import pandas as pd

def display_results():
    """
            Displays the mean score for all models-scalar combinations in a pivot table
            
    """
    mean_df = pd.DataFrame()
    id_number = 0
    for filename in os.listdir(os.path.join("data")):
        if filename.endswith("_score.csv"):
            id_number = filename[:18]
            
            results_file = os.path.join("data",str(id_number) + "_score.csv")
            results_df = pd.read_csv(results_file).dropna().round(3)
            mean_df[str(id_number)+ "_mean"] = results_df["CV_R2_mean"] 
                
    mean_df["mean"] = mean_df.mean(axis=1)
    results_file = os.path.join("data",str(id_number) + "_score.csv")
    results_df = pd.read_csv(results_file).dropna().round(3)
    temp = results_df.copy()
    temp["CV_R2_mean"] = mean_df["mean"]
    temp["model"] = results_df["Regressor_Name"].apply(lambda sen: sen.split("_")[1])
    temp["scaler"] = results_df["Regressor_Name"].apply(lambda sen: sen.split("_")[0])
    pivot_t_R2 = pd.pivot_table(temp, values='CV_R2_mean', index=["scaler"], columns=['model'], aggfunc=np.sum)
    print(pivot_t_R2)
    
if __name__ == "__main__":
	display_results()