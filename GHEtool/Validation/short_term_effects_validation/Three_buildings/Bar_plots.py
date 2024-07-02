import pandas as pd
import numpy as np
import os

import numpy as np 
import matplotlib.pyplot as plt 

# set width of bar 
barWidth = 0.25
fig = plt.subplots(figsize =(12, 8)) 

# set height of bar 
stst = [184.3, 209.2, 241] 
dynamic = [120.3, 186.3, 240] 


# Set position of bar on X axis 
br1 = np.arange(len(stst)) 
br2 = [x + barWidth for x in br1] 
br3 = [x + barWidth for x in br2] 

# Make the plot
plt.bar(br1, stst, color ='b', width = barWidth, 
         label ='Steady-state model') 
plt.bar(br2, dynamic, color ='orange', width = barWidth, 
         label ='Dynamic model') 

# Adding Xticks 

plt.ylabel('Required borehole lenght [m] ',fontsize = 18) 
plt.xticks(br1+0.125, 
        ['Auditorium', 'Office', 'Swimming pool'], fontsize = 18)

plt.legend(fontsize = 16)
plt.title('Required borehole lenghts for different buildings', fontsize = 22)
plt.show() 