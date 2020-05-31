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
id_number = 734012530000022652
results_path = os.path.join("data", "buildings_result", str(id_number) + "_results.csv")    
plot_date_and_parameter(lower_limit=None, upper_limit=1571011200000, parameter=["real_output", "RFR"], path=results_path)