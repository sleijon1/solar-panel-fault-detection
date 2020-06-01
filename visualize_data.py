import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone

def time_to_unix(year,month,day,hour):
    """Converts a given date to a unix timestamp.
    """
    date = datetime(year,month,day,hour).replace(tzinfo=timezone.utc).timestamp()
    return date*1000

def plot_date_and_parameter(lower_limit=None, upper_limit=None, parameter='real_output', path="results_sun.csv", demo=False, percentage_decrease=0):
    """Plots the choosen parameter(s) on the y-axis between the lower_limit and upper_limit unix timestamps.
    
    lower_limit -- A unix timestamp, used for a lower bound.
    upper_limit -- A unix timestamp, used for a upper bound.
    parameter   -- A specific parameter or a list of parameters from smhi.csv, e.g 'air_temperature_id' or ['air_temperature_id', 'air_pressure_id'].
    path        -- Path to the specific file containing above parameters.
    """
    df = pd.read_csv(path)
    indexes = df[(lower_limit > df['date']) | (df['date'] > upper_limit)].index
    df.drop(indexes, inplace=True)
    df['date'] = df['date'].map(lambda x: x/1000)
    df['date'] = df['date'].map(datetime.utcfromtimestamp)

    if demo:
        df['real_output'] = df['real_output'] * percentage_decrease

    #plt.plot( 'date', 'real_output', data=df, marker='o', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=4)
    plt.plot( 'date', 'real_output', data=df, marker='', color='#0083ff', linewidth=4, label="Real Output")
    plt.plot( 'date', 'RFR', data=df, marker='', color='#ff8d2e', linewidth=4, label="Predicted Output", linestyle='dashed')
    plt.xlabel('Date', fontsize=25)
    plt.ylabel('kWh', fontsize=25)
    plt.tick_params(axis='y',labelsize=20)
    plt.tick_params(axis='x',labelsize=11)
    plt.legend(loc=1, prop={'size': 20})
    
    plt.show()

def example_plot():
    plot_date_and_parameter()

if __name__ == "__main__":
    example_plot()