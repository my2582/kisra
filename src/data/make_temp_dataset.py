#!/usr/bin/env python
# coding: utf-8

# In[18]:


import pandas as pd
import numpy as np
from IPython.display import display


# ### Internal DB
# - Data of users, profiles, balance, instruments, trades and universe.

# #### Load plain data files store them into pickle formats.

# In[19]:


data_files = ['investors_m', 'profiles_m', 'profiles_s', 'balance_m', 'balance_s', 'instruments_m', 'trades', 'universe', 'constraints']
filepath = '../../data/processed/'
df = {}
for filename in data_files:
    df[filename] = pd.read_csv(filepath + filename + '.dat', header=1)
    df[filename].to_pickle(filepath + filename + '.pkl')


# In[20]:


for filename in data_files:
    display(df[filename].head())


# In[ ]:





# In[ ]:





# In[ ]:




