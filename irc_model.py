# Ignore all GPUs, tf random forest does not benefit from it.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import plot_tree
from matplotlib.pylab import rcParams

# Import data
data = pd.read_csv('input/trn_data.csv')

# Prepare data for training
# Divide the data into attributes and labels
X = data.iloc[:, 1:-1].values
y = data.iloc[:, -1].values

# Splitting the dataset into the Training set and Test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# # Feature Scaling
# sc = StandardScaler()
# X_train = sc.fit_transform(X_train)
# X_test = sc.transform(X_test)

num_estimators = 20

model = RandomForestClassifier(n_estimators=num_estimators, random_state=0)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
print(accuracy_score(y_test, y_pred))

# Extract single tree to visualize it
estimator = model.estimators_[np.random.randint(0, num_estimators)]
##set up the parameters
rcParams['figure.figsize'] = 100,100
# Export as dot file

# dot_path = 'tree.dot'
# export_graphviz(estimator,
#                 out_file=dot_path,
#                 feature_names=data.columns[:-1],
#                 class_names=['malicious', 'nonmalicious'],
#                 rounded=True, proportion=False,
#                 precision=2, filled=True)
plot_tree(estimator, feature_names=data.columns[1:-1], class_names=['malicious', 'nonmalicious'],filled=True)

plt.savefig('tree.pdf', format='pdf')
