import pandas as pd
import os
from sun_parser import SunParser
from simulate_errors import simulate_decrease
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn import metrics
import math


def train_and_predict(model_data, model_name, scaler_name):
    # Default scaler, model
    scaler = StandardScaler()
    model = RandomForestRegressor(n_estimators = 100, random_state = 42)
    
    X_train, X_test, y_train, y_test, y_test_dec = model_data[0], model_data[1], \
        model_data[2], model_data[3], model_data[4]
    if model_name == "RFR":
        model = RandomForestRegressor(n_estimators = 100, random_state = 42)
    elif model_name == "MLP":
        model = MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='sgd', alpha=0.0001 \
                             , batch_size='auto', learning_rate='adaptive', learning_rate_init=0.01, \
                             power_t=0.5, max_iter=1000, shuffle=False,random_state=0, tol=0.0001, \
                             verbose=False, warm_start=False,early_stopping=False, \
                             validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    if scaler_name == "StandardScaler":
        scaler = StandardScaler()
    elif scaler_name == "PowerTransformer-Yeo-Johnson":
        scaler = PowerTransformer(method='yeo-johnson')

    model = Pipeline([(scaler_name, scaler), (model_name, model)])
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    R2_score = metrics.r2_score(y_test, y_pred)
    R2_score_dec = metrics.r2_score(y_test_dec, y_pred)
    print("R2 score without simulating fault: " + str(R2_score) + "\nR2 score with simulated fault: "\
          + str(R2_score_dec))

    return None


def parse_and_simulate(building_id, decrease_perc):
    file_path = os.path.join("data", "buildings", str(building_id) + ".csv")
    parsed_object = SunParser(file_path)
    X, y = parsed_object.X, parsed_object.y
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, shuffle=False, random_state = 42)
    decreased_y = simulate_decrease(decrease_perc, y_test)
    model_data = (X_train, X_test, y_train, y_test, decreased_y)
    return model_data


if __name__ == '__main__':
    model_data = parse_and_simulate(734012530000000438, .5)
    train_and_predict(model_data, "RFR", "SS")
    
