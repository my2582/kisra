#!/usr/bin/env python
# coding: utf-8

# In[505]:


import numpy as np
import pandas as pd

get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '')


# ## Load external data

# In[313]:


freq = 'w'
risk_profile = 4
current_date='2020-03-30'


# #### Prices

# In[314]:


filepath = '../../data/external/'
filename = 'price_db_' + freq + '.pkl'
price_db = pd.read_pickle(filepath+filename)


# Make `df_rt`, a matrix of log returns of all eligible **instruments** in the universe with:
# - Columns: itemcode
# - Rows: date

# In[315]:


df_rt = price_db[price_db.itemtype=='ETF'].pivot(index='date', columns='itemcode', values='ret').dropna()


# ## Load portfolio constraints

# In[316]:


import riskfolio.ConstraintsFunctions as cf
import utils


# #### Load asset classification and constraints information
# - `asset_classes` <- `universe` <- tradable_instruments.pkl left join with instruments_m.pkl
# - `constraints` <- constraints.pkl

# In[317]:


# instruments_m: 투자가능 종목들 목록 (현재 시점의 거래금액, 시총 보고 뽑음)
filepath = '../../data/processed/'
filename = 'instruments_m.pkl'
instruments_m = pd.read_pickle(filepath+filename)

# simulatable_instruments: 상장된 지 3년 넘은 종목 (시뮬레이션을 위해 필요한 요건)
filepath = '../../data/external/'
filename = 'simulatable_instruments.pkl'
simulatable_instruments = pd.read_pickle(filepath+filename)

# 사용자가 지정한 제약조건 테이블. Aw>=B 형식으로 되어 있어 사람이 이해하기 편함.
filepath = '../../data/processed/'
filename = 'constraints.pkl'
df_constraints = pd.read_pickle(filepath+filename)

universe = pd.merge(simulatable_instruments, instruments_m, left_on='itemcode', right_on='itemcode', how='left')


# In[318]:


universe = universe.set_index(['itemcode'], drop=True).loc[df_rt.columns]
universe = universe.reset_index()


# In[319]:


asset_classes = utils.get_asset_classes(universe)


# #### Remove strategy constraints for now.

# In[320]:


# df_constraints = df_constraints.drop(df_constraints[df_constraints.Set=='Strategy'].index)
# df_constraints = df_constraints.drop(df_constraints[df_constraints.Set=='DC risky asset'].index)


# In[321]:


constraints = df_constraints[np.logical_or(
    df_constraints.risk_profile == str(risk_profile), df_constraints.risk_profile == 'Common')].drop(['risk_profile'], axis=1)

# constraints.loc[0, 'Type'] = 'Classes'
# constraints.loc[0, 'Weight'] = 0.4
# constraints.loc[0, 'Sign'] = '<='

# constraints.loc[10, 'Weight'] = 0.25
# constraints.loc[9, 'Factor'] = 5
# constraints.loc[11, 'Sign'] = '<='
# constraints.loc[11, 'Weight'] = 0.7
# constraints.loc[:, 'Disabled'] = False
# new_c = constraints.loc[4,:].copy()
# new_c['Sign'] = '>='
# new_c['Weight'] = 0.6
# constraints = pd.concat([pd.DataFrame(new_c).T, constraints]).reset_index(drop=True)


# In[322]:


constraints


# #### We have constraints matrice `A` and `B` such that
# - $Aw \ge B$.

# In[323]:


A, B = cf.assets_constraints(constraints, asset_classes)


# ## Estimaing mean risk portfolios

# - Using ***CDaR*** instead of variance as a risk measure.
#   - Conditional Drawdown at Risk(CDaR) is the average drawdown for all the instances that drawdown **exceeded** a certain threshold. Drawdown is a measure of downside risk.
#   - https://breakingdownfinance.com/finance-topics/alternative-investments/conditional-drawdown-at-risk-cdar/

# In[324]:


import riskfolio.Portfolio as pf
import datetime


# `y` is a matrix of log returns of all eligible instruments in the universe.

# In[325]:


current_date = '2020-06-10'
y = df_rt[df_rt.index <= current_date]


# In[326]:


df_rf = price_db[price_db.itemtype=='riskfree'].set_index('date', drop=True)
current_idx = df_rf.index.asof(datetime.datetime.strptime(current_date, '%Y-%m-%d'))
rf = df_rf.loc[current_idx].price  # risk free rate


# #### Set a log-return matrix `y`

# In[327]:


port = pf.Portfolio(returns=y, sht=False, alpha=0.05) 


# #### Set estimating methods
# - `method_mu` to estimate expected returns.
# - `method_cov` to estimated a covariance matrix.

# In[328]:


method_mu='hist'  # Method to estimate expected returns; ewma with adjust=True. See pandas.DataFrame.ewm for more details.
method_cov='oas' # Method to estimate covariance matrix; ewma with adjust=True
decay=0.97

port.assets_stats(method_mu=method_mu, method_cov=method_cov, d=decay)


# #### Apply constraints

# In[432]:


port.ainequality = A
port.binequality = B


# In[507]:


# Estimate optimal portfolio:
model='Classic' # Could be Classic (historical), BL (Black Litterman) or FM (Factor Model)
rm = 'CDaR' # Risk measure used, this time will be variance
obj = 'MaxRet' if risk_profile==4 else 'MinRisk' # Objective function, could be MinRisk, MaxRet, Utility or Sharpe

w = port.optimization(model=model, rm=rm, obj=obj, rf=rf)


# In[508]:


w = pd.merge(w, universe.loc[:,['itemcode', 'tracking_code', 'itemname']], left_index=True, right_on='itemcode', how='left')
w = w[['weights', 'tracking_code', 'itemcode', 'itemname']].set_index('itemcode', drop=True)
eps = 1e-09
w.loc[np.abs(w.weights)<eps,'weights'] = 0


# #### Put small weights (<5%) into one category, namely, others.

# In[509]:


small_wt = w[w.weights < 0.0495].weights.sum()
w_others = pd.DataFrame.from_dict(
    {'OTHERS': [w[w.weights < 0.0495].weights.sum(), 'Others', 'Others']},
    orient='index',
    columns=w.columns) if small_wt >= 0.00495 else None


# In[510]:


w_summary = pd.concat([w.drop(w[w.weights<0.0495].index), w_others])


# In[511]:


import plotly.express as px
fig = px.pie(w_summary, values='weights', names='tracking_code', title='Portfolio weights',
             labels=dict(zip(w_summary.tracking_code, w_summary.weights)), hole=0.5, width=600,
             color_discrete_sequence=px.colors.qualitative.Set3)
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.show()


# ## Show an efficient frontier

# In[512]:


points = 50 # Number of points of the frontier

frontier = port.efficient_frontier(model=model, rm=rm, points=points, rf=rf, hist=hist)

display(frontier.T.head())


# In[513]:


w


# In[514]:


w.drop('itemname', axis=1).set_index('tracking_code').T


# In[515]:


import riskfolio.PlotFunctions as plf

# Plotting the efficient frontier
label = 'Min Risk Adjusted Return Portfolio' # Title of point
mu = port.mu # Expected returns
cov = port.cov # Covariance matrix
returns = port.returns # Returns of the assets

ax = plf.plot_frontier(w_frontier=frontier, mu=mu, cov=cov, returns=returns, rm=rm,
                       rf=rf, alpha=0.05, cmap='viridis', w=w.drop('itemname', axis=1).set_index('tracking_code'), label=label,
                       marker='*', s=16, c='r', height=6, width=10, ax=None)


# In[ ]:





# In[516]:


# Risk Measures available:
#
# 'MV': Standard Deviation.
# 'MAD': Mean Absolute Deviation.
# 'MSV': Semi Standard Deviation.
# 'FLPM': First Lower Partial Moment (Omega Ratio).
# 'SLPM': Second Lower Partial Moment (Sortino Ratio).
# 'CVaR': Conditional Value at Risk.
# 'EVaR': Entropic Value at Risk.
# 'WR': Worst Realization (Minimax)
# 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
# 'ADD': Average Drawdown of uncompounded cumulative returns.
# 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
# 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
# 'UCI': Ulcer Index of uncompounded cumulative returns.

rms = ['MV', 'MAD', 'MSV', 'FLPM', 'SLPM', 'CVaR',
       'EVaR', 'WR', 'MDD', 'ADD', 'CDaR', 'UCI', 'EDaR']

w_s = pd.DataFrame([])

for i in rms:
    w = port.optimization(model=model, rm=i, obj=obj, rf=rf, l=l, hist=hist)
    w_s = pd.concat([w_s, w], axis=1)
    
w_s.columns = rms


# In[517]:


w_s.style.format("{:.2%}").background_gradient(cmap='YlGn')


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




