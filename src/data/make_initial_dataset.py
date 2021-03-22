#!/usr/bin/env python
# coding: utf-8

# In[18]:


import pandas as pd
import numpy as np
from IPython.display import display


# Initial data
# - Data of users, profiles, balance, instruments, trades and universe.

data_files = ['investors_m', 'profiles_m', 'profiles_s', 'balance_m', 'balance_s', 'instruments_m', 'trades', 'universe', 'constraints']
filepath = '../../data/processed/'
df = {}
for filename in data_files:
    df[filename] = pd.read_csv(filepath + filename + '.dat', header=1)
    df[filename].to_pickle(filepath + filename + '.pkl')
    print('Pickled: {}'.format(filename))

data_files = ['simulatable_instruments']
filepath = '../../data/external/'
df = {}
for filename in data_files:
    df[filename] = pd.read_csv(filepath + filename + '.dat', header=1)
    df[filename].to_pickle(filepath + filename + '.pkl')
    print('Pickled: {}'.format(filename))

print('Completed.')