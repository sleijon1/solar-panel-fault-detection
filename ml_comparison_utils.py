from __future__ import print_function
import numpy as np
import pandas as pd
from sklearn import model_selection
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import StandardScaler, MaxAbsScaler, MinMaxScaler, RobustScaler, QuantileTransformer, \
    PowerTransformer
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.preprocessing import PolynomialFeatures 
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics
import os

def print_results(names, results, RMSE, R2_score):
    print()
    print("#" * 30 + "Results" + "#" * 30)
    counter = 0

    class Color:
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        DARKCYAN = '\033[36m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

    # Get max row
    clf_names = set([name.split("_")[1] for name in names])
    max_mean = {name: 0 for name in clf_names}
    max_mean_counter = {name: 0 for name in clf_names}
    for name, result in zip(names, results):
        counter += 1
        clf_name = name.split("_")[1]
        if result.mean() > max_mean[clf_name]:
            max_mean_counter[clf_name] = counter
            max_mean[clf_name] = result.mean()

    # print max row in BOLD
    counter = 0
    prev_clf_name = names[0].split("_")[1]
    for name, result, RMSE, R2_score in zip(names, results, RMSE, R2_score):
        counter += 1
        clf_name = name.split("_")[1]
        if prev_clf_name != clf_name:
            print()
            prev_clf_name = clf_name
        msg = "%s: %f (%f) [RMSE:%.3f] [R2_score:%.3f]" % (name, result.mean(), result.std(), RMSE, R2_score)
        if counter == max_mean_counter[clf_name]:
            print(Color.BOLD + msg)
        else:
            print(Color.END + msg)


def create_pipelines(verbose=1):
    """
         Creates a list of pipelines with preprocessing(PCA), models and scalers.

    :return:
    """
    
     
    models = [
              #('LR', LinearRegression()),
              #('PR', LinearRegression()),
              ('DTR', DecisionTreeRegressor(max_depth = 10, random_state = 42)),
              ('MLP',MLPRegressor(hidden_layer_sizes=(100,),  activation='logistic', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='adaptive', learning_rate_init=0.01, power_t=0.5, max_iter=1000, shuffle=False,random_state=0, tol=0.0001, verbose=False, warm_start=False,early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08)),
              ('RFR',RandomForestRegressor(n_estimators = 100, random_state = 42)),
              #('LASSO',Lasso(alpha=0.1))
              ]
    scalers = [
                ('StandardScaler', StandardScaler()),
               ('MinMaxScaler', MinMaxScaler()),
               ('MaxAbsScaler', MaxAbsScaler()),
               ('RobustScaler', RobustScaler()),
               ('QuantileTransformer-Normal', QuantileTransformer(output_distribution='normal')),
               ('QuantileTransformer-Uniform', QuantileTransformer(output_distribution='uniform')),
               ('PowerTransformer-Yeo-Johnson', PowerTransformer(method='yeo-johnson')),
               ('Normalizer', Normalizer())
               ]
               
    additions = [
                 ]
    # Create pipelines
    pipelines = []
    for model in models:
        # Append only model
        model_name = "_" + model[0]
        pipelines.append((model_name, Pipeline([model])))

        # Append model+scaler
        for scalar in scalers:
            model_name = scalar[0] + "_" + model[0]
            pipelines.append((model_name, Pipeline([scalar, model])))

        # To easier distinguish between with and without Additions (i.e: PCA)
        # Append model+addition
        for addition in additions:
            model_name = "_" + model[0] + "-" + addition[0]
            pipelines.append((model_name, Pipeline([addition, model])))

        # Append model+scaler+addition
        for scalar in scalers:
            for addition in additions:
                model_name = scalar[0] + "_" + model[0] + "-" + addition[0]
                pipelines.append((model_name, Pipeline([scalar, addition, model])))

    if verbose:
        print("Created these pipelines:")
        for pipe in pipelines:
            print(pipe[0])

    return pipelines


def run_cv_and_test(X_train, y_train, X_test, y_test, pipelines, scoring,seed, num_folds,
                    dataset_name, n_jobs):
    """

        Iterate over the pipelines, calculate CV mean and std scores, fit on train and predict on test.
        Return the results in a dataframe

    """

    # List that contains the rows for a dataframe
    rows_list = []

    # Lists for the pipeline results
    results = []
    names = []
    RMSE = []
    R2_scores = []
    df = pd.DataFrame()
    curr_R2_score = 0
    curr_RMSE = 0
    prev_clf_name = pipelines[0][0].split("_")[1]

    df["date"] = X_test["date"]
    df["real_output"] = y_test
    X_train.drop("date", axis=1)
    X_test.drop("date", axis=1)
    print("First name is : ", prev_clf_name)

    for name, model in pipelines:
        kfold = model_selection.KFold(n_splits=num_folds, random_state=seed, shuffle=True)
        cv_results = model_selection.cross_val_score(model, X_train, y_train, cv=kfold, n_jobs=n_jobs, scoring=scoring)
        results.append(cv_results)
        names.append(name)

        # Print CV results of the best CV classier
        msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
        print(msg)
        print(name)

        # fit on train and predict on test
        column = []
        if name.find("PR") != -1:
            poly = PolynomialFeatures(degree = 4) 
            X_poly = poly.fit_transform(X_train) 
  
            model.fit(X_poly, y_train) 
            y_pred = model.predict(poly.fit_transform(X_test))
            y_pred = y_pred.clip(min=0)
            curr_RMSE = metrics.mean_squared_error(y_test, y_pred)
            curr_R2_score = metrics.r2_score(y_test, y_pred)
            column = y_pred.tolist()
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_pred = y_pred.clip(min=0)
            curr_RMSE = metrics.mean_squared_error(y_test, y_pred)
            curr_R2_score = metrics.r2_score(y_test, y_pred)
            column = y_pred.tolist()

        RMSE.append(curr_RMSE)
        R2_scores.append(curr_R2_score)
        # Add separation line if different classifier applied
        rows_list, prev_clf_name = check_seperation_line(name, prev_clf_name, rows_list)

        # Add for final dataframe
        results_dict = {"Dataset": dataset_name,
                        "Classifier_Name": name,
                        "CV_mean": cv_results.mean(),
                        "CV_std": cv_results.std(),
                        "RMSE": curr_RMSE,
                        "R2_score": curr_R2_score
                        }
        rows_list.append(results_dict)
        if name[0] == '_':
            name = name[1:]
        
        df[name] = column
    
    print_results(names, results, RMSE, R2_scores)
    path = os.path.join("data", "results_sun.csv")
    df.to_csv(path)

    df = pd.DataFrame(rows_list)
    return df[["Dataset", "Classifier_Name", "CV_mean", "CV_std", "RMSE", "R2_score"]]



def check_seperation_line(name, prev_clf_name, rows_list):
    """
        Add empty row if different classifier ending

    """

    clf_name = name.split("_")[1]
    if prev_clf_name != clf_name:
        empty_dict = {"Dataset": "",
                      "Classifier_Name": "",
                      "CV_mean": "",
                      "CV_std": "",
                      "Test_acc": ""
                      }
        rows_list.append(empty_dict)
        prev_clf_name = clf_name
    return rows_list, prev_clf_name
