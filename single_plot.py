# -*- coding: utf-8 -*-
"""
Created on Mon May  4 11:01:28 2020

@author: Jonat
"""
from __future__ import print_function

import os
from visualize_data import plot_date_and_parameter

"""
            Plots the real output and the predicted output for a chosen model-scalar combination
"""
results_path = os.path.join("data", "results_sun.csv")    
plot_date_and_parameter(parameter=["real_output", "StandardScaler_KNN"], path=results_path)