import pandas as pd
import os


def simulate_decrease(per_decrease, y_test):
    decreased_output = per_decrease*y_test
    return decreased_output

if __name__ == '__main__':
    print("Invoking simulating_errors as main wtf")
