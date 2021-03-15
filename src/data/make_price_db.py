#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from IPython.display import display


# ## External DB
# ### 1) **Tradable** instruments
# - Filtering conditions:
# 
# - e.g.: `itemtype` may be ETF, stocks and etc.

# In[2]:


itemtype = 'ETF'


# #### Load external data formatted as plain files, and then pickle them.
# - We <span class="mark">drop</span> any instrument if:
#   - `min_datapoints`: <span class="mark"># of data points <= 3-year long.</span>

# In[3]:


data_files = ['price_d', 'volume_d', 'price_w', 'volume_w', 'price_m', 'volume_m']
filepath = '../../data/external/'
df = {}
for filename in data_files:
    df[filename] = pd.read_csv(filepath + filename + '.dat', header=7)
    df[filename].drop(range(0,6), inplace=True)
    df[filename].rename(columns={'Code': 'date'}, inplace=True)
    df[filename].date = pd.to_datetime(df[filename].date)
    name_cols = df[filename].columns[1:]
    df[filename][name_cols] = df[filename][name_cols].apply(pd.to_numeric, errors='coerce', axis=1)


# #### Merge data sets and melt them into one tall and this data frame.
# - `df_db[freq]` is your final data frame.
#   - `freq` = {d|w|m} for different frequencies.
# - df_db[freq].`trading_amt_mln` is a thre-month average trading amount.

# In[4]:


df_pr = {}
df_vol = {}
df_db = {}

frequency = ['d', 'w', 'm']
# We need an extra 1 record for return calcaultion.
min_datapoints = {'d': 365*3+1, 'w': 52*3+1, 'm': 12*3+1}
window_3m = {'d': 90, 'w': 12, 'm': 3}

for freq in frequency:
    pr = df['price_'+freq].dropna(thresh=min_datapoints[freq], axis=1).dropna()
    vol = df['volume_'+freq].dropna(thresh=min_datapoints[freq], axis=1).dropna()
    df_pr[freq] = pd.melt(pr, id_vars=['date'], var_name='itemcode', value_name='price')
    df_vol[freq] = pd.melt(vol, id_vars=['date'], var_name='itemcode', value_name='volume')
    df_db[freq]= pd.merge(df_pr[freq], df_vol[freq], left_on=['date', 'itemcode'], right_on=['date', 'itemcode'], how='outer')
    df_db[freq] = df_db[freq].assign(trading_amt_mln=(df_db[freq].price*df_db[freq].volume).divide(10**6).rolling(window_3m[freq], min_periods=1).mean())
    df_db[freq] = df_db[freq].assign(ret=np.log(1+df_db[freq].groupby('itemcode').price.pct_change()))
    df_db[freq]['itemtype'] = itemtype
#     df_db[freq].to_pickle(filepath + 'price_db_' + freq + '.pkl')


# ### 2) **Non-tradable** instruments
# - e.g.: rates

# In[5]:


df['ecos_w'] = pd.read_csv(filepath + 'ecos_w' + '.dat', header=3, parse_dates=['date'])
df['ecos_w']['itemcode'] = 'CALL'
df['ecos_w']['itemtype'] = 'riskfree'
df['ecos_w'].rename(columns={'call':'price'}, inplace=True)


# In[6]:


df_db['w'] = pd.concat([df_db['w'], df['ecos_w']])


# ## Pickle final restuls

# `price_db_#.pkl`

# In[7]:


for freq in frequency:
    df_db[freq].to_pickle(filepath + 'price_db_' + freq + '.pkl')


# `tradable_instruments.pkl`

# In[8]:


df_tradables = df_db['w'][df_db['w'].itemtype=='ETF']
tradable_instruments = df_tradables.loc[df_tradables.date==df_tradables.date.max()].drop(['date', 'ret'], axis=1).reset_index(drop=True)
tradable_instruments.to_pickle(filepath + 'tradable_instruments.pkl')


# In[9]:


for freq in frequency:
    display(df_db[freq])


# In[10]:


display(tradable_instruments)


# In[ ]:




