from __future__ import print_function

import os
from sklearn.model_selection import train_test_split
from sklearn.utils.validation import column_or_1d
from sun_parser import SunParser
from ml_comparison_utils import (create_pipelines, run_cv_and_test)
from display_results import display_results
# Global_vars
num_folds = 10
n_jobs = -1
is_save_results = True


if __name__ == '__main__':
    """
            -For all different id numbers in the folder, do CV and generate R2 score. 
            -For all mode-scalar combinations, display the mean R2 score for all the id numbers 
            -Write these R2 scores to a csv file
        """
    #For all data files in the folder
    for filename in os.listdir(os.path.join("data")):
        if filename.endswith("_new.csv"):
            id_number = filename[:18]
            path = os.path.join("data",(str(id_number) + "_new.csv"))
            # Read datasets
            parser = SunParser(path)
            scoring = parser.metric
            print("")
            print("Working on " + str(id_number) + " dataset")
            
            X, y = parser.X, parser.y
        
            y_sun = column_or_1d(y, warn=False)
            #create train and test set
            X_train, X_test, y_train, y_test = train_test_split(X, y_sun, test_size=0.20, shuffle=False, random_state = 42)
            pipelines = create_pipelines()
            
            # Run CV together with a test on the test set
            results_df = run_cv_and_test(X_train, y_train, X_test, y_test, pipelines, scoring,1234,num_folds,id_number)
            
            
            # Save cv experiment to csv
            if is_save_results:
                score_name = str(id_number) + "_score.csv"
                score_path = os.path.join("data",score_name)
                results_df.to_csv(score_path, index=False)
                
    print("\n"+"Displays the mean of all R2_scores for all datasets used")
    display_results()
            
    
