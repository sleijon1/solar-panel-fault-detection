import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


def logistic_reg():
	# Load csv
	df_train = pd.read_csv("/path/to/data.csv")

	# Split dataframe into X and y
	y = df_train['Motion.mode']
	X = df_train.drop("Motion.mode", axis=1)

	# Split into train and test sets
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

	# Logistic Regression
	logisticRegr = LogisticRegression()
	logisticRegr.fit(X_train, y_train)
	score = logisticRegr.score(X_test, y_test)
	return score

def main():
	f1_score = logistic_reg()
	print(f1_score)

if __name__ == "__main__":
	main()