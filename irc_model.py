# Ignore all GPUs, tf random forest does not benefit from it.
import os

import pandas as pd
from sklearn.model_selection import train_test_split

os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Import data
data = pd.read_csv('input/trn_data.csv')

# Extract feature and target np arrays (inputs for placeholders)
input_x = data.iloc[:, 0:-1].values
input_y = data.iloc[:, -1].values

# Splitting the dataset into the Training set and Test set
X_train, X_test, y_train, y_test = train_test_split(input_x, input_y, test_size=0.25, random_state=0)
