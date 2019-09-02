 import os
from sklearn.impute import SimpleImputer 
import pandas as pd

INPUT_PATH = os.path.expanduser('~/Documents/Work/Stratosphere/Masters-thesis/IRC-Malware-Detection/input') 
CSV_PATH = os.path.join(INPUT_PATH, 'trn_data_per.csv') 
CSV_PATH_NEW = '/Users/preneond/Documents/Work/Stratosphere/Masters-thesis/IRC-Malware-Detection/input/trn_data_per_new.csv' 

df = pd.read_csv(CSV_PATH, delimiter=';')                                                                                                                                                                                       
imp = SimpleImputer(strategy="mean") 
ii = imp.fit_transform(df)          
df = pd.DataFrame(ii[:,1:], columns=cols)     
df.round({'periodicity':4}) 
df.to_csv(CSV_PATH_NEW, encoding='utf-8', sep=';')  
 
 