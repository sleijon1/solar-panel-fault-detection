import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone

def time_to_unix(year,month,day,hour):
    """Converts a given date to a unix timestamp.
    """
    date = datetime(year,month,day,hour).replace(tzinfo=timezone.utc).timestamp()
    return date*1000

def plot_date_and_parameter(lower_limit=None, upper_limit=None, parameter='real_output', path="results_sun.csv"):
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
    #parameter = ["real_output"]+ list(df.columns)[2:]
    df.plot(x='date',y=parameter)
    plt.show()

def example_plot():
    plot_date_and_parameter()

if __name__ == "__main__":
    example_plot()