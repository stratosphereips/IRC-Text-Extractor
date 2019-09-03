import os
from sklearn.impute import SimpleImputer 
import pandas as pd

INPUT_PATH = os.path.expanduser('~/Documents/Work/Stratosphere/Masters-thesis/IRC-Malware-Detection/input') 
CSV_PATH = os.path.join(INPUT_PATH, 'trn_data_per.csv') 

cols = ['periodicity', 'duration', 'pkt_size', 'msg_count', 'src_ports_count', 'dst_port', 'src_spec_chars',
            'msg_spec_chars', 'msg_word_entropy', 'malicious']

df = pd.read_csv(CSV_PATH, delimiter=';')                                                                                                                                                                                     
imp = SimpleImputer(strategy="mean")
ii = imp.fit_transform(df)          
df = pd.DataFrame(ii[:,1:], columns=cols)     
df.round({'periodicity':4}) 
df.to_csv(CSV_PATH, encoding='utf-8', sep=';')  