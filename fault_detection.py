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
import matplotlib.pyplot as plt
import math
from statistics import mean


def detect_error(decreased_y, predicted_y):
    time_horizon = 7 * 24
    all_values = []
    
    if time_horizon > len(decreased_y):
        return 0
    else:
        for i in range(0, len(decreased_y)-time_horizon):
            decreased_window = decreased_y[i:i+time_horizon] 
            predicted_window = predicted_y[i:i+time_horizon]
            
            
            mean_list = []
            for d_w, p_w in zip(decreased_window, predicted_window):
                if d_w == 0 and p_w == 0:
                    mean_list.append(0)
                elif d_w == 0:
                    mean_list.append(0)
                else:
                    mean_list.append(p_w-d_w)
            if not (mean(decreased_window) == 0):
               error_percent = ((mean(mean_list)/mean(predicted_window))* 100)
               if error_percent > threshold:
                   days_gone = ((i+time_horizon) / 24)
                   return True, days_gone
               
    
    #plt.plot(all_values)
    #plt.show()
    return False, -1



def train_and_predict(model_data, model_name, scaler_name):
    # Default scaler, model
    scaler = StandardScaler()
    model = RandomForestRegressor(n_estimators = 100, random_state = 42)
    date_test = pd.DataFrame()
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
    #fig, ax = plt.subplots()
    #ax.plot(y_test.values.tolist())
    #ax.plot(y_pred)
    #ax.plot(y_test_dec)

    
    
    R2_score = metrics.r2_score(y_test, y_pred)
    R2_score_dec = metrics.r2_score(y_test_dec, y_pred)
    print("R2 score without simulating fault: " + str(R2_score) + "\nR2 score with simulated fault: "\
          + str(R2_score_dec))

    return y_pred


def parse_and_simulate(building_id, decrease_perc):
    file_path = os.path.join("data", "buildings", str(building_id) + ".csv")
    parsed_object = SunParser(file_path)
    X, y = parsed_object.X, parsed_object.y
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, shuffle=False, random_state = 42)
    
    #X_train = X
    #X_test = X
    #y_train = y
    #y_test = y
    
    decreased_y = simulate_decrease(decrease_perc, y_test)
    
    date_test = pd.DataFrame()
    date_test["date"] = X_test["date"]
    X_train.drop("date", axis=1)
    X_test.drop("date", axis=1)
    date = date_test["date"].values.tolist()
    model_data = (X_train, X_test, y_train, y_test, decreased_y, date)
    return model_data


if __name__ == '__main__':
    decrease_list = [(0, 1, 0.6)]
    real_fault = 0
    fake_news = 0
    empty_life = 0
    mean_days_gone = []
    for filename in os.listdir(os.path.join("data", "buildings")):
        if filename.endswith(".csv") and not filename.endswith("734012530000024618.csv") and not filename.endswith("734012530000027879.csv") and not filename.endswith("734012530000027909.csv"):
            id_number = filename[:18]
            model_data = parse_and_simulate(id_number, decrease_list)
            threshold = 50
            decreased_y = model_data[4]
            real_y = model_data[3]
            predicted_y = train_and_predict(model_data, "RFR", "SS")
            
            decreased_error_found, days_gone_decreased = detect_error(decreased_y, predicted_y)
            real_error_found, days_gone_real = detect_error(real_y, predicted_y)
            
            
            print(str(id_number))
            if decreased_error_found and not real_error_found:
                print("Real fault found in " + str(days_gone_decreased) + " days")
                mean_days_gone.append(days_gone_decreased)
                real_fault +=1
            elif real_error_found:
                print("Preexisting fault found in " + str(days_gone_real) + " days")
                fake_news +=1
            elif not decreased_error_found and not real_error_found:
                print("No faults found")
                empty_life +=1
            else:
                print("dunno")
    print("Real_faults found: " + str(real_fault))
    print("Fake faults found: " + str(fake_news))
    print("Nothing found: " + str(empty_life))
    print("Average days til error found: " + str(mean(mean_days_gone)))
                
