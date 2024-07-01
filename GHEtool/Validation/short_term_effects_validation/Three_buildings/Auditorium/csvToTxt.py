import pandas as pd
import numpy as np
import os

data = pd.read_csv(os.path.join(os.path.dirname(__file__),"auditorium_one_column.csv"),comment='#',sep=";",header=None,)

heat = data[0].tolist()
print(heat)
heat_20y=[]
for i in range(20):
    heat_20y  = heat_20y +heat

time = [3600*i for i in range(8760*20)]
full_data = np.stack([time, heat_20y], axis=1)

np.savetxt(os.path.join(os.path.dirname(__file__),'audit_test.txt'), full_data, delimiter="\t",fmt='%f')