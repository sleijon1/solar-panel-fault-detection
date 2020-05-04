from __future__ import print_function

import os
from sklearn.model_selection import train_test_split
from sklearn.utils.validation import column_or_1d
from sun_parser import SunParser
from ml_comparison_utils import (create_pipelines, run_cv_and_test)
from visualize_data import plot_date_and_parameter
# Global_vars
num_folds = 10
n_jobs = -1
is_save_results = True


if __name__ == '__main__':


        # Read datasets
    parser = SunParser()
    scoring = parser.metric
    print("Working on " + parser.name + " dataset")
    print("Metric: ")
    X, y = parser.X, parser.y

    y_sun = column_or_1d(y, warn=False)
    X_train, X_test, y_train, y_test = train_test_split(X, y_sun, test_size=0.30, shuffle=False, random_state = 42)

    # Create pipelines
    pipelines = create_pipelines()

    # Run cv experiment without hyper_param_tuning
    results_df = run_cv_and_test(X_train, y_train, X_test, y_test, pipelines, scoring,1234,num_folds,
                                     dataset_name=parser.name, n_jobs=n_jobs)

    # Save cv experiment to csv
    if is_save_results:
        score_name = parser.name + "_score.csv"
        score_path = os.path.join("data",score_name)
        results_df.to_csv(score_path, index=False)
    

