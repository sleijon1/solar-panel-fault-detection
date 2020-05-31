from __future__ import print_function
import numpy as np
import pandas as pd
from sklearn import model_selection
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import StandardScaler, MaxAbsScaler, MinMaxScaler, RobustScaler, QuantileTransformer, \
    PowerTransformer
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn import metrics
import os
from sklearn import neighbors

"Parts of the code is taken from https://github.com/shaygeller/Normalization_vs_Standardization by Shay Geller"

def create_pipelines(verbose=1):
    """
         Creates a list of pipelines with models and scalers.
         verbose -- to print or not to print, 1 or 0
    :return:
    """

    models = [
              #('LR', LinearRegression()),
              #('DTR', DecisionTreeRegressor(max_depth = 10, random_state = 42)),
              #('MLP',MLPRegressor(hidden_layer_sizes=(100,),  activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='adaptive', learning_rate_init=0.01, power_t=0.5, max_iter=1000, shuffle=False,random_state=0, tol=0.0001, verbose=False, warm_start=False,early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08)),
              ('RFR',RandomForestRegressor(n_estimators = 100, random_state = 42)),
              #('LASSO',Lasso(alpha=0.1))
              #('KNN',neighbors.KNeighborsRegressor(n_neighbors = 10, weights = "distance", algorithm = "ball_tree"))
              #('GPR', GaussianProcessRegressor())
              ]
    scalers = [
               #('StandardScaler', StandardScaler()),
               #('MinMaxScaler', MinMaxScaler()),
               #('MaxAbsScaler', MaxAbsScaler()),
               #('RobustScaler', RobustScaler()),
               #('QuantileTransformer-Normal', QuantileTransformer(output_distribution='normal')),
               #('QuantileTransformer-Uniform', QuantileTransformer(output_distribution='uniform')),
               #('PowerTransformer-Yeo-Johnson', PowerTransformer(method='yeo-johnson')),
               #('Normalizer', Normalizer())
               ]
               
    # Create pipelines
    pipelines = []

    for model in models:
        model_name = "_" + model[0]
        pipelines.append((model_name, Pipeline([model])))
        # Append model+scaler
        for scalar in scalers:
            model_name = scalar[0] + "_" + model[0]
            pipelines.append((model_name, Pipeline([scalar, model])))

    return pipelines


def run_cv_and_test(X_train, y_train, X_test, y_test, pipelines, scoring,seed, num_folds, id_number, n_jobs = -1):
    """

        Iterate over the pipelines, calculate R2-score for the CV, fit on train and predict on test.
        Return the results in a dataframe.
        
        Write all predictions to a csv file.
        
        As a sideeffect the predictions for each model-scalar is written to a file
        X_train -- The X for the training set, A dataframe where each column is a parameter and each row is a datapoint
        y_train -- The y for the training set, An array where each value is the output for a datapoint
        X_test -- The X for the test set, A dataframe where each column is a parameter and each row is a datapoint
        y_test -- The y for the test set, An array where each value is the output for a datapoint
        pipelines -- The pipelines containing all model-scalar combinations 
        scoring -- The scoring metric used for evaluation, e.g. 'r2' for R2-score or 'neg_root_mean_squared_error' for RMSE
        seed -- The random_state seed used in kfold
        num_folds -- Number of folds in the kfold
        id_number -- The id for the dataset that is currently running

    """
    #ignores div by 0 errors as to nut clutter the output
    np.seterr(divide = 'ignore') 

    rows_list = []
    names = []
    test_scores = []
    R2_scores = []
    results_df = pd.DataFrame()
    prev_clf_name = pipelines[0][0].split("_")[1]

    #removing the unix time stamp from the data and putting it in the results dataframe
    results_df["date"] = X_test["date"]
    results_df["real_output"] = y_test
    X_train.drop("date", axis=1)
    X_test.drop("date", axis=1)

    for name, model in pipelines:
        print("\tPerforming KFold cross-validation.")
        kfold = model_selection.KFold(n_splits=num_folds, random_state=seed, shuffle=True)
        cv_results = model_selection.cross_val_score(model, X_train, y_train, cv=kfold, n_jobs=n_jobs, scoring=scoring)
        R2_scores.append(cv_results.mean())
        names.append(name)

        print("\tFitting the model on the training set.")
        model.fit(X_train, y_train)
        print("\tPredicting on the test set.")
        y_pred = model.predict(X_test)
        #all negative values are corrected to 0
        y_pred = y_pred.clip(min=0)
        curr_R2_score = metrics.r2_score(y_test, y_pred)
        predictions = y_pred.tolist()
        test_scores.append(curr_R2_score)
        
        
        # Add separation line if different classifier applied
        rows_list, prev_clf_name = check_seperation_line(name, prev_clf_name, rows_list)

        # Add for final dataframe
        results_dict = {"Dataset": str(id_number),
                        "Regressor_Name": name,
                        "CV_R2_mean": cv_results.mean()
                        }
        rows_list.append(results_dict)
        if name[0] == '_':
            name = name[1:]
        
        results_df[name] = predictions
    
    for name,R2_score,test_score in zip(names, R2_scores, test_scores):
        #msg = "%s: R2-score:%f Test score:%f" % (name, R2_score, test_score)
        print("R2-scores: ")
        print("\tKFold:    " + str(round(R2_score,4)))
        print("\tTest set: " + str(round(test_score,4)))
    
    
    path = os.path.join("data", "buildings_result", str(id_number) + "_results.csv")
    results_df.to_csv(path)

    df = pd.DataFrame(rows_list)
    return df[["Dataset", "Regressor_Name", "CV_R2_mean"]]



def check_seperation_line(name, prev_clf_name, rows_list):
    """
        Add empty row if different model-scalar ending (If new model, add new row)
        name -- model-scalar name
        prev_clf_name -- previous model-scalar name
        rows_list -- The list containing the result_dictionary
    """

    clf_name = name.split("_")[1]
    if prev_clf_name != clf_name:
        empty_dict = {"Dataset": "",
                      "Regressor_Name": "",
                      "CV_R2_Mean": "",
                      }
        rows_list.append(empty_dict)
        prev_clf_name = clf_name
    return rows_list, prev_clf_name
