import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

def find_changepoints(df):
    changepoints = []
    target_word = df['value'][0]
    anchor = 0
    for i,word in enumerate(df['value']):
        if word == target_word:
            changepoints.append(anchor)
        else:
            anchor+=1
            changepoints.append(anchor)
        target_word = word
    scaled_changepoints = np.array(changepoints)/(max(changepoints)-min(changepoints))
    output = []
    for i in scaled_changepoints:
        output.append(i if i is 0 or 1 else 0.5)
    return output


count = 0
reports = [f for f in os.listdir('reports') if os.path.isfile(os.path.join('reports',f))]

for report in reports:
    df = pd.read_csv(f'reports/{report}')
    df['changepoints'] = find_changepoints(df)
    df.to_feather(f'data/{report}.feather')  
    count+=1
    print(f'==={count}/{len(reports)}===')



