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
import os.path


# In[ ]:


# Manually assign column names from bundle_description.txt file
colnames = ['number', 'name', 'full_name', 'axis_AU', 'eccentricity', 'inclination',
            'type', 'companions', 'magnitude', 'abs_magnitude', 'abs_magnitude_err', 
            'diameter_km', 'e_diameter_err1', 'e_diameter_err2', 'e_diameter_notecode', 
            'p_diameter', 'p_diameter_err1', 'p_diameter_err2', 'p_diameter_notecode',
            'c_diameter', 'c_diameter_err1', 'c_diameter_err2', 'c_diameter_notecode',
            'albedo', 'albedo_err1', 'albedo_err2', 'albedo_notecode', 'albedo_colorcode', 
            'density', 'density_err1', 'density_err2', 'density_notecode', 
            'methods_da', 'methods_density', 'reference'
           ]

diams = pd.read_csv('./data/diameters/tno-centaur_diam-albedo-density/data/tno_centaur_diam_alb_dens.tab', 
                    header=None, sep='\t', encoding='latin-1')

display(diams.head())
diams = diams[0].str.split(expand=True)
diams[2] = diams[2] + diams[3]
diams.drop([3], inplace=True, axis=1)

diams.columns = colnames
display(diams.head())

diams = diams[['number', 'name', 'full_name', 'type', 'diameter_km', 'p_diameter']]
diams['diameter_km'] = diams['diameter_km'].astype(float)
diams['p_diameter'] = diams['p_diameter'].astype(float)
diams.loc[~(diams['diameter_km'] > 0), 'diameter_km']=np.nan
diams.loc[~(diams['p_diameter'] > 0), 'p_diameter']=np.nan
diams['diameter_km'] = diams['diameter_km'].fillna(diams['p_diameter'])
diams = diams[~pd.isnull(diams['diameter_km'])]

diams.set_index(['number', 'name', 'full_name', 'type'], inplace=True)
diams = diams.groupby(['number', 'name', 'full_name', 'type']).median()
diams = diams.reset_index()
diams['name'] = diams['name'].str.replace('-', '')
diams.loc[diams['name'] == 'Pluto', 'full_name'] = '134340Pluto'
diams.drop(['p_diameter'], axis=1, inplace=True)

display(diams.head())
savename = './data/diameters/TNO_Centaurs.csv'
if not os.path.isfile(savename):
    diams.to_csv(savename, index=False)

print(len(diams), 'unique asteroids')


# In[ ]:


df = pd.read_csv('./data/all_asteroids.csv', low_memory=False)
df['full_name'] = df['full_name'].str.replace(' ', '').str.replace('(', '').str.replace(')', '').str.replace('-', '')
display(df.tail())

diams = pd.read_csv('./data/diameters/TNO_Centaurs.csv', low_memory=False)
diams.drop(['number', 'name', 'type'], axis=1, inplace=True)
df = pd.merge(df, diams, on='full_name', how='left')
display(df.tail())

print(len(df[~pd.isnull(df['diameter_km'])]), 'diameter values that can be joined')
original = len(df[~pd.isnull(df['diameter'])])
df['diameter'] = df['diameter'].fillna(df['diameter_km'])
print(len(df[~pd.isnull(df['diameter'])])-original, 'new diameter values added')
df.drop(['diameter_km'], inplace=True, axis=1)

savename = './data/all_asteroids_wrangled.csv'
if not os.path.isfile(savename):
    df.to_csv(savename, index=False)
display(df.tail())


# In[ ]:


# Check that Pluto has been added appropriately
df[df['full_name'] == '134340Pluto']


# In[ ]:




