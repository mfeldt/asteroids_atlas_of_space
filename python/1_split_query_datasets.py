#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Watermark is not required for this code, but is included for information. 
import watermark
get_ipython().run_line_magic('load_ext', 'watermark')
get_ipython().run_line_magic('watermark', '-a "ELEANOR LUTZ" -d -v -iv -m')


# In[ ]:


import numpy as np
import pandas as pd
from astropy.time import Time, TimeDelta
import os.path


# In[ ]:


def get_angle(x0, y0, x1, y1):
    ''' Calculate the angle from horizontal, counterclockwise '''
    angle = np.rad2deg(np.arctan2(y1-y0, x1-x0))
    return angle

def split_asteroids(readname, savename, min_distance, max_distance, 
                    min_diameter, max_diameter, start_date, stop_date, 
                    randomize=False):
    print(savename.split('/')[-1])
    df = pd.read_csv(readname, low_memory=False)
    print('Original dataset contains', len(df), 'items')

    # SPLIT BY DISTANCE FROM SUN, AU
    df['q'] = pd.to_numeric(df['q'])
    df = df[df['q'] < max_distance]
    df = df[df['q'] >= min_distance]
    print('Dataset now contains', len(df), 'items', min_distance, '~', 
          max_distance, 'AU from the sun')

    # SPLIT BY DIAMETER, KM
    if min_diameter != 'null':
        df = df[df['diameter'].astype(float) >= min_diameter]
        df = df[df['diameter'].astype(float) < max_diameter]
    else:
        df = df[pd.isnull(df['diameter'])]
        exclude = ['GRK', 'TJN', 'MBA']
        df = df[~df['class'].isin(exclude)]
        
    print('Dataset now contains', len(df), 'items', min_diameter, '~', 
          max_diameter, 'km in diameter') 
    
    assert df['spkid'].isna().sum() == 0
    df['horizons'] = "DES=+"+df['spkid'].astype(str)
    
    # REMOVE DUPLICATES
    count = len(df)
    df = df.drop_duplicates(keep='first', subset='spkid')
    print('Dropped', count-len(df), 'duplicated rows by spkid')
    print(len(df[df.duplicated('horizons') == True]), 
          'duplicated rows remaining by horizons')
    
    # ADD DATETIME LIMITS
    print('Dropped', len(df[df['per'].isna()]), "NaN values in period data")
    df = df[np.isfinite(df['per'])]
    
    if randomize != False: 
        df_named = df[~pd.isnull(df['name'])].copy()
        df_notnamed = df[pd.isnull(df['name'])].copy()
        if len(df_named) < randomize:
            df_sample = df_notnamed.sample(n=randomize-len(df_named))
            df = pd.concat([df_sample, df_named])
        else:
            df = df_named.sample(n=randomize)
        assert len(df) == randomize
        print(len(df_named), 'named asteroids included in randomized set')
    
    df1 = df[df['per'] < 40*365].copy()
    df1['timedelta'] = TimeDelta(df1['per']*0.25*24*60*60, format='sec')
    df1['begin_time'] = Time(Time(start_date, format="iso") - df1['timedelta']).value
    df1.drop('timedelta', axis=1, inplace=True)
    print(len(df1), 'values truncated because orbital period is shorter than 40 years')
    
    df2 = df[df['per'] >= 40*365].copy()
    df2['begin_time'] = Time(stop_date, format="iso").value
    df = pd.concat([df1, df2])
    df['end_time'] = Time(start_date, format="iso").value
    
    df['end_time'] = pd.to_datetime(df['end_time'], dayfirst=False).dt.strftime('%Y-%m-%d-%H-%M-%S')
    df['begin_time'] = pd.to_datetime(df['begin_time'], dayfirst=False).dt.strftime('%Y-%m-%d-%H-%M-%S')
    
    print('Dataset has', len(df), 'items total,', 
          len(df[df['name'] != np.nan]), 'with proper names.')
    
    if not os.path.isfile(savename):
        df.to_csv(savename, index=False)
    else:
        print('---NOT SAVED BECAUSE FILE ALREADY EXISTS---\n')
    
def split_planets(readname, savename, start_date, stop_date):
    
    print(savename.split('/')[-1])
    df = pd.read_csv(readname, low_memory=False)
    print('Original dataset contains', len(df), 'items')

    # ADD DATETIME LIMITS
    print('Dropped', len(df[df['per'].isna()]), "NaN values in period data")
    df = df[np.isfinite(df['per'])]
    
    df['timedelta'] = TimeDelta(df['per']*1*24*60*60, format='sec')
    df['begin_time'] = Time(Time(start_date, format="iso") - df['timedelta']).value
    df['end_time'] = Time(start_date, format="iso").value
    df.drop('timedelta', axis=1, inplace=True)
    
    df['end_time'] = pd.to_datetime(df['end_time'], dayfirst=False).dt.strftime('%Y-%m-%d-%H-%M-%S')
    df['begin_time'] = pd.to_datetime(df['begin_time'], dayfirst=False).dt.strftime('%Y-%m-%d-%H-%M-%S')
            
    # DUPLICATES
    print(len(df[df.duplicated('horizons') == True]), 'duplicated rows remaining by horizons')
    print('Dataset has', len(df), 'items total,', 
          len(df[df['name'] != np.nan]), 'with proper names.')
    
    if not os.path.isfile(savename):
        df.to_csv(savename, index=False)
    else:
        print('---NOT SAVED BECAUSE FILE ALREADY EXISTS---\n')


# In[ ]:


'''
Select asteroids by size and distance from the sun 
Note: objects are selected by perihelion distance,
so they may not be in visible range after getting the exact 
orbital locations from HORIZONS.
'''
start_date = '2000-01-01 00:00:00'
stop_date = '1990-01-01 00:00:00'

# PLANETS
readname = './data/planets.csv'
savename = './data/planets.csv'
split_planets(readname, savename, start_date, stop_date)

# ASTEROIDS 
readname = './data/all_asteroids_wrangled.csv'
readname_comets = './data/all_comets_wrangled.csv'

# ASTEROIDS >20KM in DIAMETER
savename = './data/large_asteroids.csv'
min_diameter, max_diameter = 20, np.inf
min_distance, max_distance = 0, 240
split_asteroids(readname, savename, min_distance, max_distance, 
                min_diameter, max_diameter, start_date, stop_date)

# ASTEROIDS 10~20KM in DIAMETER
savename = './data/small_asteroids.csv'
min_diameter, max_diameter = 10, 20
min_distance, max_distance = 0, 240
split_asteroids(readname, savename, min_distance, max_distance, 
                min_diameter, max_diameter, start_date, stop_date)

# COMETS >10KM in DIAMETER
savename = './data/large_comets.csv'
min_diameter, max_diameter = 10, np.inf
min_distance, max_distance = 0, 240
split_asteroids(readname_comets, savename, min_distance, max_distance, 
                min_diameter, max_diameter, start_date, stop_date)

# ASTEROIDS
savename = './data/any_outer_asteroids.csv'
min_diameter, max_diameter = 'null', 'null'
min_distance, max_distance = 3, 240
split_asteroids(readname, savename, min_distance, max_distance, 
               min_diameter, max_diameter, start_date, stop_date, randomize=5000)

# ASTEROIDS
savename = './data/any_inner_asteroids.csv'
min_diameter, max_diameter = 'null', 'null'
min_distance, max_distance = 0, 2.5
split_asteroids(readname, savename, min_distance, max_distance, 
                 min_diameter, max_diameter, start_date, stop_date, randomize=3000)


# In[ ]:


# Output the different classes of asteroids and comets for reference

ast = pd.read_csv('./data/large_asteroids.csv', low_memory=False)
display(ast['class'].value_counts())

ast = pd.read_csv('./data/small_asteroids.csv', low_memory=False)
display(ast['class'].value_counts())

ast = pd.read_csv('./data/any_outer_asteroids.csv', low_memory=False)
display(ast['class'].value_counts())

ast = pd.read_csv('./data/any_inner_asteroids.csv', low_memory=False)
display(ast['class'].value_counts())

com = pd.read_csv('./data/large_comets.csv', low_memory=False)
display(com['class'].value_counts())


# In[ ]:


df_asts = pd.read_csv('./data/large_asteroids.csv')
df_tjn = df_asts[df_asts['class'] == 'TJN'].copy()
df_non_tjn = df_asts[df_asts['class'] != 'TJN'].copy()
count, t = 0, 0
indices = []

for index, row in df_tjn.iterrows():
    filename = "./data/large_asteroids/"+row['horizons']+".csv"
    try:
        df = pd.read_csv(filename)
        xs, ys = df["X"].tolist(), df["Y"].tolist()
        theta = [get_angle(0, 0, x, y) for x, y in zip(xs, ys)]
        theta = [np.radians(x) for x in theta]
        if theta[-1] > 0.6294830920687847:
            df_tjn.loc[index, 'class'] = 'GRK'
            t += 1
    except:
        count += 1

df = pd.concat([df_tjn, df_non_tjn])
df.to_csv('./data/large_asteroids.csv', index=False)
print(len(df[df['class'] == 'GRK']), 'GRKs')


# In[ ]:


df_asts = pd.read_csv('./data/small_asteroids.csv')
df_tjn = df_asts[df_asts['class'] == 'TJN'].copy()
df_non_tjn = df_asts[df_asts['class'] != 'TJN'].copy()
count, t = 0, 0
indices = []

for index, row in df_tjn.iterrows():
    filename = "./data/small_asteroids/"+row['horizons']+".csv"
    try:
        df = pd.read_csv(filename)
        xs, ys = df["X"].tolist(), df["Y"].tolist()
        theta = [get_angle(0, 0, x, y) for x, y in zip(xs, ys)]
        theta = [np.radians(x) for x in theta]
        
        # Angle of Jupiter position (found after HORIZONS search)
        if theta[-1] > 0.6294830920687847:
            df_tjn.loc[index, 'class'] = 'GRK'
            t += 1
    except:
        count += 1

df = pd.concat([df_tjn, df_non_tjn])
df.to_csv('./data/small_asteroids.csv', index=False)
print(len(df[df['class'] == 'GRK']), 'GRKs')


# In[ ]:




