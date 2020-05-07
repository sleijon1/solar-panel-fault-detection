# -*- coding: utf-8 -*-
"""
Created on Mon May  4 11:01:28 2020

@author: Jonat
"""
from __future__ import print_function

import os
from visualize_data import plot_date_and_parameter
results_path = os.path.join("data", "results_sun.csv")    
plot_date_and_parameter(parameter=["real_output", "PowerTransformer-Yeo-Johnson_RFR"], path=results_path)