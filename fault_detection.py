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


def detect_error(decreased_y, predicted_y, threshold, time_horizon=7*24):
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

def create_confusion_matrix(threshold, results):
    counter = [0, 0, 0]
    for key in results.keys():
        if key[1] == threshold:
            counter = [a + b for a, b in zip(counter, results[key])]
    return counter

def evaluate_fault_detection():
    decrease_lists = [[(0, 1, .4)], [(0, 1, .5)], [(0, 1, .6)], [(0, 1, .7)], \
                      [(0, 1, .8)], [(0, 1, .9)]]
    thresholds = [35, 40, 45, 50, 55, 60]
    results = {}
    time_horizon = 7*24
    for filename in os.listdir(os.path.join("data", "buildings")):
        if filename.endswith(".csv") and not filename.endswith("734012530000024618.csv") and not filename.endswith("734012530000027879.csv") and not filename.endswith("734012530000027909.csv"):
            id_number = filename[:18]
            for decrease in decrease_lists:
                model_data = parse_and_simulate(id_number, decrease)
                decreased_y = model_data[4]
                real_y = model_data[3]
                perc_decrease = decrease[0][2]
                predicted_y = train_and_predict(model_data, "RFR", "SS")
                for threshold in thresholds:
                    key = (perc_decrease, threshold, time_horizon)
                    try:
                        test = results[key]
                    except KeyError:
                        results[key] = [0, 0, 0]
                        
                    decreased_error_found, days_gone_decreased = detect_error(decreased_y, \
                                                                              predicted_y, threshold, time_horizon)
                    real_error_found, days_gone_real = detect_error(real_y, predicted_y, threshold, time_horizon)
                    
                    if decreased_error_found and not real_error_found:
                        results[key][0] += 1
                    elif real_error_found:
                        results[key][1] += 1
                    elif not decreased_error_found and not real_error_found:
                        results[key][2] += 1

                    print("id: " + str(id_number) + ", decrease: " + str(perc_decrease) + ", threshold: " + str(threshold))
    
    for threshold in thresholds:
        matrix = create_confusion_matrix(threshold, results)
        print("Threshold: " + str(threshold) + ", Matrix: " + str(matrix))
    return None


def run_fault_detection():
    decrease_list = [(0, 1, 0.6)]
    true_positive = 0
    false_positive = 0
    false_negative = 0
    mean_days_gone = []
    for filename in os.listdir(os.path.join("data", "buildings")):
        if filename.endswith(".csv") and not filename.endswith("734012530000024618.csv") and not filename.endswith("734012530000027879.csv") and not filename.endswith("734012530000027909.csv"):
            id_number = filename[:18]
            model_data = parse_and_simulate(id_number, decrease_list)
            threshold = 50
            decreased_y = model_data[4]
            real_y = model_data[3]
            predicted_y = train_and_predict(model_data, "RFR", "SS")
            
            decreased_error_found, days_gone_decreased = detect_error(decreased_y, predicted_y, threshold)
            real_error_found, days_gone_real = detect_error(real_y, predicted_y, threshold)
            
            
            print(str(id_number))
            if decreased_error_found and not real_error_found:
                print("True positive found in " + str(days_gone_decreased) + " days")
                mean_days_gone.append(days_gone_decreased)
                true_positive +=1
            elif real_error_found:
                print("False positive found in " + str(days_gone_real) + " days")
                false_positive +=1
            elif not decreased_error_found and not real_error_found:
                print("False negative found")
                false_negative +=1
            else:
                print("dunno")
    print("true_positives found: " + str(true_positive))
    print("Fake faults found: " + str(false_positive))
    print("Nothing found: " + str(false_negative))
    print("Average days til error found: " + str(mean(mean_days_gone)))
                

if __name__ == '__main__':
    evaluate_fault_detection()
