import pandas as pd
from src.models.load_data import Balance, Instruments, AdvisedPortfolios, PriceDB, Singleton
from src.models.utils import get_current_port, get_advised_port, get_recommendation
from DataBase import databaseDF
from datetime import datetime
import copy
import re
from src.models.portfolio import Portfolio
from src.models.load_data import Singleton, Balance
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import cm
import scipy.stats as st
import riskfolio.RiskFunctions as rk
from src.models.asset import Asset
from pypfopt.discrete_allocation import DiscreteAllocation


class Character:
    def __init__(self, characters):
        self.options = characters
        self.db = databaseDF()
        self.file_name = 'profiles_m.pkl'
        self.scoring = {
            1: '안정',
            2: '안정추구',
            3: '위험중립',
            4: '적극투자',
            5: '공격투자'
        }

    def empty_check(self):
        for content in self.options:
            if not content:
                return False
        return True

    # def get_detail(self, new_units, prices, remaining_cash):
    #     # c_date: 추천 포트폴리오DB에서 사용자가 입력한 날짜와 가장 가까운 날짜.
    #     c_date = self.advised_pf.loc[self.advised_pf.date <=
    #                                  self.current_date, ['date']].max().date
    #     df = self.advised_pf.loc[(self.advised_pf.date == c_date) & (
    #         self.advised_pf.risk_profile == self.risk_profile), :]

    #     # 보유수량
    #     detail = pd.DataFrame.from_dict(
    #         new_units, orient='index').rename(columns={0: 'quantity'})
    #     detail.index.name = 'itemcode'

    #     # 매입가격
    #     temp = pd.DataFrame.from_dict(prices, orient='index').rename(
    #         columns={0: 'cost_price'}).drop([1], axis=1)
    #     temp.index.name = 'itemcode'

    #     # 병합
    #     detail = detail.merge(temp, left_index=True,
    #                           right_index=True, how='inner')

    #     instruments_m = Instruments.instance().data
    #     detail['price'] = detail['cost_price']
    #     detail['cost_value'] = detail['quantity']*detail['cost_price']
    #     detail['value'] = detail['quantity'] * \
    #         detail['cost_price']  # 매입가와 평가가격 동일하다고 가정
    #     detail = detail.merge(instruments_m.loc[:, [
    #                           'itemcode', 'itemname', 'asset_class']], left_on='itemcode', right_on='itemcode', how='left')
    #     detail = detail.reset_index(drop=True)

    #     # 잔액으로 현금 레코드 기록
    #     df_cash = {
    #         'itemcode': 'C000001',
    #         'quantity': remaining_cash,
    #         'cost_price': 1,
    #         'cost_value': remaining_cash,
    #         'price': 1,
    #         'value': remaining_cash,
    #         'itemname': '현금',
    #         'asset_class': 'Cash'
    #     }
    #     df_cash = pd.DataFrame.from_dict(df_cash, orient='index').T

    #     detail = pd.concat([detail, df_cash])
    #     detail['date'] = c_date
    #     detail['date'] = pd.to_datetime(
    #         detail['date'], format='%Y-%m-%d').dt.strftime('%m/%d/%Y 4:0:00 PM').astype(str)
    #     detail['userid'] = self.userid
    #     detail['name'] = self.username
    #     detail['group_by'] = ''
    #     detail['original'] = 'N'

    #     # 종목비중 구하기
    #     detail['wt'] = detail.value.transform(lambda x: x/x.sum())

    #     detail = detail.reset_index(drop=True)

    #     return detail

    # def plot_hist(self, returns, w, alpha=0.05, bins=50, height=6, width=10, ax=None):
    #     r"""
    #     Create a histogram of portfolio returns with the risk measures.

    #     Parameters
    #     ----------
    #     returns : DataFrame
    #         Assets returns.
    #     w : DataFrame of shape (n_assets, 1)
    #         Portfolio weights.
    #     alpha : float, optional
    #         Significante level of VaR, CVaR and EVaR. The default is 0.05.
    #     bins : float, optional
    #         Number of bins of the histogram. The default is 50.
    #     height : float, optional
    #         Height of the image in inches. The default is 6.
    #     width : float, optional
    #         Width of the image in inches. The default is 10.
    #     ax : matplotlib axis, optional
    #         If provided, plot on this axis. The default is None.

    #     Raises
    #     ------
    #     ValueError
    #         When the value cannot be calculated.

    #     Returns
    #     -------
    #     ax : matplotlib axis.
    #         Returns the Axes object with the plot for further tweaking.

    #     Example
    #     -------
    #     ::

    #         ax = plf.plot_hist(returns=Y, w=w1, alpha=0.05, bins=50, height=6,
    #                         width=10, ax=None)

    #     .. image:: images/Histogram.png

    #     Source: https://riskfolio-lib.readthedocs.io/en/latest/_modules/PlotFunctions.html#plot_series

    #     """

    #     if not isinstance(returns, pd.DataFrame):
    #         raise ValueError("returns must be a DataFrame")

    #     if not isinstance(w, pd.DataFrame):
    #         raise ValueError("w must be a DataFrame")

    #     if w.shape[1] > 1 and w.shape[0] == 0:
    #         w = w.T
    #     elif w.shape[1] > 1 and w.shape[0] > 0:
    #         raise ValueError("w must be a  DataFrame")

    #     if returns.shape[1] != w.shape[0]:
    #         a1 = str(returns.shape)
    #         a2 = str(w.shape)
    #         raise ValueError("shapes " + a1 + " and " + a2 + " not aligned")

    #     if ax is None:
    #         ax = plt.gca()
    #         fig = plt.gcf()
    #         fig.set_figwidth(width)
    #         fig.set_figheight(height)

    #     a = np.array(returns, ndmin=2) @ np.array(w, ndmin=2)
    #     ax.set_title("Portfolio Returns Histogram")
    #     n, bins1, patches = ax.hist(
    #         a, bins, density=1, edgecolor="skyblue", color="skyblue", alpha=0.5
    #     )
    #     mu = np.mean(a)
    #     sigma = np.std(a, axis=0, ddof=1).item()
    #     risk = [
    #         mu,
    #         mu - sigma,
    #         mu - rk.MAD(a),
    #         -rk.VaR_Hist(a, alpha),
    #         -rk.CVaR_Hist(a, alpha),
    #         -rk.EVaR_Hist(a, alpha)[0],
    #         -rk.WR(a),
    #     ]
    #     label = [
    #         "Mean: " + "{0:.2%}".format(risk[0]),
    #         "Mean - Std. Dev.("
    #         + "{0:.2%}".format(-risk[1] + mu)
    #         + "): "
    #         + "{0:.2%}".format(risk[1]),
    #         "Mean - MAD("
    #         + "{0:.2%}".format(-risk[2] + mu)
    #         + "): "
    #         + "{0:.2%}".format(risk[2]),
    #         "{0:.2%}".format((1 - alpha)) + " Confidence VaR: " + "{0:.2%}".format(risk[3]),
    #         "{0:.2%}".format((1 - alpha))
    #         + " Confidence CVaR: "
    #         + "{0:.2%}".format(risk[4]),
    #         "{0:.2%}".format((1 - alpha))
    #         + " Confidence EVaR: "
    #         + "{0:.2%}".format(risk[5]),
    #         "Worst Realization: " + "{0:.2%}".format(risk[6]),
    #     ]
        
    #     return label, fig

    # def get_ordersheets(self, tag=None):
    #     balance = self.db.getUserBalance(userid=self.userid)

    #     print('balance[0] is '.format(balance[0]))
    #     balance_date = balance[0][0]

    #     self.price_db = PriceDB.instance().data
    #     # self.price_db.loc[self.price_db.date == balance_date]
    #     # self.price_db.loc[self.price_db.date == self.current_date]

    #     try:
    #         balance_date = datetime.strptime(
    #             balance_date, '%Y-%m-%d %H:%M:%S %p').strftime('%Y-%m-%d')
    #     except:
    #         balance_date = datetime.strptime(
    #             balance_date, '%m/%d/%Y %H:%M:%S %p').strftime('%Y-%m-%d')

    #     print('balance_date: {}'.format(balance_date))

    #     balance = pd.DataFrame(balance, columns=['date', 'userid', 'name', 'asset_class', 'itemcode', 'itemname',
    #                                              'quantity', 'cost_price', 'cost_value', 'price', 'value', 'wt', 'group_by', 'original'])
    #     balance = balance.drop(['price'], axis=1)
    #     print('---balance---')
    #     print(balance)

    #     new_port = get_advised_port(
    #         risk_profile=self.risk_profile, df_advised_ports=self.advised_pf)

    #     old_new = pd.merge(balance.loc[:, ['itemcode', 'quantity', 'value', 'wt']], new_port.loc[:, ['itemcode', 'wt']],
    #                        left_on=['itemcode'], right_on=['itemcode'], how='outer', suffixes=['_old', '_new'])

    #     old_new.loc[:, ['value', 'wt_old', 'quantity', 'wt_new']] = old_new.loc[:, [
    #         'value', 'wt_old', 'quantity', 'wt_new']].fillna(value=0)

    #     assets = old_new.loc[(old_new.itemcode != 'C000001')
    #                          & (old_new.itemcode != 'D000001'), :]
    #     cash = old_new.loc[(old_new.itemcode == 'C000001') |
    #                        (old_new.itemcode == 'D000001'), :]
    #     old_assets = assets.drop(['wt_new'], axis=1)
    #     # old_assets = old_assets.rename(columns={'price_old':'price', 'wt_old':'wt'})
    #     old_cash = cash.drop(['wt_new'], axis=1)
    #     # old_cash = old_cash.rename(columns={'price_old':'price', 'wt_old':'wt'})
    #     old_tickers = assets.itemcode.tolist()
    #     old_quantities = assets.quantity.astype(int).tolist()
    #     assets = assets.merge(self.price_db.loc[self.price_db.date == balance_date, ['itemcode', 'price']],
    #                           left_on='itemcode', right_on='itemcode', how='left', suffixes=('', '_db'))
    #     # assets.loc[:, 'price'] = assets['price'].fillna(assets['self.price_db'])

    #     old_prices = assets.price.tolist()
    #     cash_amounts = cash.value.tolist()
    #     cash_currency = ['KRW']*len(cash_amounts)

    #     p = Portfolio()
    #     p.easy_add_assets(tickers=old_tickers,
    #                       quantities=old_quantities, prices=old_prices)
    #     p.easy_add_cash(amounts=cash_amounts, currencies=cash_currency)
    #     p.selling_allowed = True

    #     new_tickers = old_new.loc[(old_new.itemcode != 'CASH') & (
    #         old_new.itemcode != 'DEPOSIT'), 'itemcode'].tolist()
    #     # 단위가 %이므로 100을 곱한다.
    #     new_wt = (old_new.loc[(old_new.itemcode != 'CASH') & (
    #         old_new.itemcode != 'DEPOSIT'), 'wt_new']*100).tolist()

    #     # price_cur = self.price_db.loc[self.price_db.date == balance_date, ['itemcode', 'price']]
    #     # for ticker in new_tickers:
    #     #     p.add_asset(Asset(ticker=ticker, price=price_cur.loc[price_cur.itemcode==ticker, 'price']))

    #     target_asset_alloc = dict(zip(new_tickers, new_wt))

    #     print('----target_asset_alloc----')
    #     print(target_asset_alloc)

    #     # p.rebalance() returns a tuple of:
    #     # * new_units (Dict[str, int]): Units of each asset to buy. The keys of the dictionary are the tickers of the assets.
    #     # * prices (Dict[str, [float, str]]): The keys of the dictionary are the tickers of the assets. Each value of the dictionary is a 2-entry list. The first entry is the price of the asset during the rebalancing computation. The second entry is the currency of the asset.
    #     # * remaining_cash (float): The remaining cash after rebalancing.
    #     # * max_diff (float): Largest difference between target allocation and optimized asset allocation.
    #     (new_units, prices, remaining_cash, max_diff) = p.rebalance(
    #         target_asset_alloc, verbose=True)

    #     # 리밸런싱을 실행하기 위한 주문내역을 detail 테이블에 넣기 위하여 df 로 받음.
    #     new_detail = self.get_detail(new_units, prices, remaining_cash)

    #     print('********리밸런싱 태그 달림********{}'.format(tag))
    #     new_detail['original'] = tag if tag is not None else 'N'

    #     new_general = new_detail.loc[:, ['wt', 'value', 'asset_class']].groupby(
    #             'asset_class').sum().sort_values('wt', ascending=False).reset_index()
    #     new_general['userid'] = new_detail.userid[0]
    #     new_general['date'] = new_detail.date[0]


    #     # detail 테이블에 기록
    #     self.db.insert_detail(new_detail)

    #     # general 테이블에 기록
    #     self.db.insert_general(new_general)

    #     return (new_units, prices, remaining_cash)

    # def calculate_ordersheet(self, port, trading_amt):
    #     return None

    # def simulate_trades(self, first_trade=False, new_units=None, prices=None, remaining_cash=None):
    #     if first_trade:
    #         price_db = PriceDB.instance().data

    #         # 최근 잔고 가져오기
    #         # 아직 어떤 타입으로 가져오는지 모름
    #         detail = self.db.getUserBalance(userid=self.userid)       
    #         detail = pd.DataFrame(detail, columns=['date', 'userid', 'name', 'asset_class', 'itemcode', 'itemname',
    #                                              'quantity', 'cost_price', 'cost_value', 'price', 'value', 'wt', 'group_by', 'original'])

    #         next_detail = copy.deepcopy(detail)   # 현재 잔고를 일단 다음 단계 잔고로 복사해 두고
    #         all_the_nexts = pd.DataFrame(columns=next_detail.columns)
    #         for dt in dates:
    #             prices_dt = price_db.loc[price_db.date==dt, ['price', 'itemcode']].reset_index(drop=True)
    #             holding_itemcodes = detail.itemcode.to_list()
    #             holding_prices = prices_dt[prices_dt.itemcode.isin(holding_itemcodes)]
    #             next_date = datetime.strptime(dt, '%Y-%m-%d')
    #             next_date = str(next_date.month)+'/'+str(next_date.day)+'/'+str(next_date.year)+' 04:00:00 PM'
    #             next_detail = copy.deepcopy(next_detail)
    #             next_detail.merge(holding_prices, left_on='itemcode', right_on='itemcode', how='left', suffixes=('_old', '')).drop('price_old', axis=1)
    #             next_detail.loc[next_detail.itemcode=='C000001', 'price'] = 1
    #             next_detail['date'] = next_date
    #             all_the_nexts = pd.concat((all_the_nexts, next_detail))

    #         all_the_nexts = all_the_nexts.reset_index(drop=True)
    #         print(all_the_nexts)
            
    #         # detail 테이블에 기록
    #         self.db.insert_detail(all_the_nexts)


    #         # 추천 포트폴리오DB에서 사용자가 입력한 날짜와 가장 가까운 날짜.

    #         self.current_date = self.advised_pf.loc[self.advised_pf.date <= self.current_date, [
    #             'date']].max().date



    #         # new_port: self.current_date 기준 추천 포트폴리오
    #         new_port = self.advised_pf.loc[(self.advised_pf.date==self.current_date) & (self.advised_pf.risk_profile==self.risk_profile), :]

    #         # 최근 잔고 가져오기
    #         # 아직 어떤 타입으로 가져오는지 모름
    #         balance = self.db.getUserBalance(userid=self.userid)       
    #         balance = pd.DataFrame(balance, columns=['date', 'userid', 'name', 'asset_class', 'itemcode', 'itemname',
    #                                              'quantity', 'cost_price', 'cost_value', 'price', 'value', 'wt', 'group_by', 'original'])

    #         # 비중 정보만 있는 port를 trading_amt 금액만큼 산다고 할 때, 종목별 수량과 잔액 구하기
    #         new_units, remaining_cash = self.calculate_ordersheet(port = new_port, trading_amt = balance.value.sum())

    #         # 매매하고 detail 테이블에 넣기 위한 매매결과를 dataframe 리턴받음
    #         detail = self.get_detail(new_units, prices, remaining_cash)



    #         df = self.advised_pf.loc[(self.advised_pf.date == self.current_date) & (
    #             self.advised_pf.risk_profile == self.risk_profile), :]

    #         print('The date we are looking for is {}'.format(self.current_date))

    #         first_advised_port = copy.deepcopy(df)
    #         first_advised_port = first_advised_port.loc[:, ['weights', 'itemname']].groupby(
    #             'itemname').sum().reset_index()
    #         by_assetclass = df.loc[:, ['weights', 'asset_class']].groupby(
    #             'asset_class').sum().sort_values('weights', ascending=False).reset_index()

    #         # print('self.options is {}'.format(self.options))
    #         # print('첫 추천포트폴리오(risk profile {}):'.format(self.risk_profile))
    #         # print(first_advised_port)

    #         new_units, prices, remaining_cash = self.get_ordersheets()
    #         # print('---new_units---')
    #         # print(new_units)
    #         # print('---prices----')
    #         # print(prices)

    #         return first_advised_port, by_assetclass, new_units, prices, remaining_cash
    #     else:
    #         dates = self.advised_pf.loc[(self.advised_pf.risk_profile == self.risk_profile) & (
    #             self.advised_pf.date > self.current_date), 'date'].unique()
    #         every20day = dates[20::20]

    #         price_db = PriceDB.instance().data

    #         # 최근 잔고 가져오기
    #         # 아직 어떤 타입으로 가져오는지 모름
    #         detail = self.db.getUserBalance(userid=self.userid)       
    #         detail = pd.DataFrame(detail, columns=['date', 'userid', 'name', 'asset_class', 'itemcode', 'itemname',
    #                                              'quantity', 'cost_price', 'cost_value', 'price', 'value', 'wt', 'group_by', 'original'])

    #         next_detail = copy.deepcopy(detail)   # 현재 잔고를 일단 다음 단계 잔고로 복사해 두고
    #         all_the_nexts = pd.DataFrame(columns=next_detail.columns)
    #         for dt in dates:
    #             prices_dt = price_db.loc[price_db.date==dt, ['price', 'itemcode']].reset_index(drop=True)
    #             holding_itemcodes = detail.itemcode.to_list()
    #             holding_prices = prices_dt[prices_dt.itemcode.isin(holding_itemcodes)]
    #             next_date = datetime.strptime(dt, '%Y-%m-%d')
    #             next_date = str(next_date.month)+'/'+str(next_date.day)+'/'+str(next_date.year)+' 09:00:00 AM'
    #             next_detail = copy.deepcopy(next_detail)
    #             next_detail.merge(holding_prices, left_on='itemcode', right_on='itemcode', how='left', suffixes=('_old', '')).drop('price_old', axis=1)
    #             next_detail.loc[next_detail.itemcode=='C000001', 'price'] = 1
    #             next_detail['date'] = next_date
    #             all_the_nexts = pd.concat((all_the_nexts, next_detail))

    #         all_the_nexts = all_the_nexts.reset_index(drop=True)
    #         print(all_the_nexts)
            
    #         # detail 테이블에 기록
    #         self.db.insert_detail(all_the_nexts)

  
    #         # # 최근 잔고 가져오기
    #         # # 아직 어떤 타입으로 가져오는지 모름
    #         # balance = self.db.getUserBalance(userid=self.userid)       
    #         # balance = pd.DataFrame(balance, columns=['date', 'userid', 'name', 'asset_class', 'itemcode', 'itemname',
    #         #                                      'quantity', 'cost_price', 'cost_value', 'price', 'value', 'wt', 'group_by', 'original'])

    #         # # print('here- balance.columns is {}:'.format(balance.columns))
    #         # # print(balance)

    #         # next_balance = copy.deepcopy(balance)
    #         # # all_the_nexts = pd.DataFrame(columns=next_balance.columns)

    #         # price_db = PriceDB.instance().data

    #         # for idx, dt in enumerate(dates):
    #         #     # self.current_date = dt  # 현재 날짜기준으로 리밸런싱
    #         #     ## 리밸런싱 주기가 왔으면 ##
    #         #     if dt in every20day:
    #         #         ## 리밸런싱 후 다음 날짜로
    #         #         # df = self.advised_pf.loc[(self.advised_pf.date == self.current_date) & (
    #         #         #     self.advised_pf.risk_profile == self.risk_profile), :]


    #         #         new_units, prices, remaining_cash = self.get_ordersheets(tag='Rebal')

    #         #         print('리밸런싱 포트폴리오(risk profile {}):'.format(self.risk_profile))
    #         #         print('---new_units---')
    #         #         print(new_units)
    #         #         print('---prices----')
    #         #         print(prices)


    #         #         continue

    #         #     # 최근 잔고가져오기
    #         #     # 아직 어떤 타입으로 가져오는지 모름
    #         #     balance = self.db.getUserBalance(userid=self.userid)
    #         #     # df로 타입을 바꿈
    #         #     balance = pd.DataFrame(balance, columns=['date', 'userid', 'name', 'asset_class', 'itemcode', 'itemname',
    #         #                                         'quantity', 'cost_price', 'cost_value', 'price', 'value', 'wt', 'group_by', 'original'])

    #         #     print('after pd.DataFrame, balance is')
    #         #     print(balance)

    #         #     # 매일 종가 업데이트

    #         #     if idx+1 >= dates.shape[0]:
    #         #         break
                
    #         #     # next_date = dates[idx+1]
    #         #     next_date = dt

    #         #     print('다음 날 잔고-merge 이전')
    #         #     print(next_balance.loc[:, ['date','userid','itemcode','price','wt','original']])

    #         #     print('현재 날짜 {}'.format(self.current_date))
    #         #     print('내일 날짜 {}'.format(next_date))
    #         #     prices_dt = price_db.loc[price_db.date == next_date, [
    #         #         'price', 'itemcode']].reset_index(drop=True)

    #         #     balance = balance.set_index('itemcode')
    #         #     prices_dt = prices_dt.set_index('itemcode')

    #         #     next_balance = balance.merge(prices_dt.price, left_index=True, right_index=True, how='left', suffixes=('_old', '')).drop(['price_old'], axis=1)
                
    #         #     # itemcode 컬럼 다시 가져오기
    #         #     next_balance = next_balance.reset_index()

    #         #     # next_balance = next_balance.merge(prices_dt, left_on='itemcode', right_on='itemcode',
    #         #     #                    how='left', suffixes=('_old', '')).drop('price_old', axis=1)
    #         #     # next_balance = next_balance.merge(prices_dt, left_on='itemcode', right_on='itemcode',
    #         #     #     how='left', suffixes=('_x', '_y'))
    #         #     print('next_date: {}'.format(next_date))
    #         #     print('다음 날 잔고-merge 이후')
    #         #     print(next_balance)
    #         #     # holding_itemcodes = balance.itemcode.to_list()
    #         #     # holding_prices = prices_dt[prices_dt.itemcode.isin(
    #         #     #     holding_itemcodes)]
    #         #     # print('holding_prices:')
    #         #     # print(holding_prices)
    #         #     next_date = datetime.strptime(next_date, '%Y-%m-%d')
    #         #     next_date = str(next_date.month)+'/'+str(next_date.day) + \
    #         #         '/'+str(next_date.year)+' 4:00:00 PM'
    #         #     next_balance['date'] = next_date
    #         #     next_balance.loc[next_balance.itemcode =='C000001', 'price'] = 1

    #         #     # 종목별 평가액 업데이트
    #         #     next_balance['value'] = next_balance['price']*next_balance['quantity']
    #         #     print('next_balance.price')
    #         #     print(next_balance.price)

    #         #     # print('next_balance.columns are {}'.format(next_balance.columns))
    #         #     self.db.insert_detail(next_balance)

    #         #     new_general = next_balance.loc[:, ['wt', 'value', 'asset_class']].groupby(
    #         #             'asset_class').sum().sort_values('wt', ascending=False).reset_index()
    #         #     new_general['userid'] = next_balance.userid[0]
    #         #     new_general['date'] = next_balance.date[0]

    #         #     # general 테이블에 기록
    #         #     self.db.insert_general(new_general)

    #         #     # all_the_nexts = pd.concat((all_the_nexts, next_balance))

    #         # # all_the_nexts = all_the_nexts.reset_index(drop=True)

    #         # # print(all_the_nexts)
    #         # # detail 테이블에 기록
    #         # # self.db.insert_detail(all_the_nexts)

    #     return new_units, prices, remaining_cash

    def rebalance(self, rebal_date, price_d, detail, new_port):
        '''
        Rebalance a portfolio.
        
        Parameters:
        rebal_date: str
            rebalancing date
        
        detail: DataFrame
        current balance
        
        price_d: DataFrame
        price data on rebal_date
        
        new_port: DataFrame
        A new portfolio. Your current portfolio in `detail` will be rebalanced toward `new_port`.
        '''
        trading_amt = detail.value.sum()

        print('new_port', new_port)
        print('detail', detail)
        print('price_d', price_d)
        print('rebal_date: {}'.format(rebal_date))
        print('trading_amt: {}'.format(trading_amt))
        
        wt = new_port[['itemcode', 'weights']].set_index('itemcode').to_dict()['weights']
        pr = new_port[['itemcode', 'price']].set_index('itemcode').squeeze()
        da = DiscreteAllocation(weights=wt, latest_prices=pr, total_portfolio_value=trading_amt)
        
        allocation, remaining_cash = da.greedy_portfolio()
        print("리밸런싱 결과:")
        print("{}: 새 포트폴리오(종목코드:수량)-{}".format(rebal_date,allocation))
        print(" - 매매 후 잔액: {:.2f} KRW".format(remaining_cash))
        
        # 매매한 뒤의 레코드 생성
        df_qty = pd.DataFrame.from_dict(allocation, orient='index', columns=['quantity'])
        next_detail = new_port.merge(df_qty, left_on='itemcode', right_index=True, how='inner')
        next_detail['cost_price'] = next_detail.price.copy()   
        next_detail['cost_value'] = next_detail.cost_price*next_detail.quantity
        next_detail['value'] = next_detail.cost_value.copy()
        
        # 매매하고 남은 돈은 현금으로
        df_cash = {
            'itemcode': 'C000001',
            'quantity': remaining_cash,
            'cost_price': 1,
            'price':1,
            'cost_value': remaining_cash,
            'value': remaining_cash,
            'itemname': '현금',
            'asset_class': 'Cash'
        }
        df_cash = pd.DataFrame.from_dict(df_cash, orient='index').T
        
        next_detail = pd.concat((next_detail[['itemcode', 'quantity', 'cost_price', 'price', 'cost_value', 'value',
        'itemname', 'asset_class']], df_cash), axis=0)
        
        next_detail['wt'] = next_detail.value/next_detail.value.sum()
        next_date = datetime.strptime(rebal_date, '%Y-%m-%d')
        #next_date = str(next_date.month)+'/'+str(next_date.day)+'/'+str(next_date.year)+' 03:30:00 PM'
        next_detail['date'] = next_date
        next_detail.reset_index(drop=True, inplace=True)
        next_detail['group_by'] = ''
        next_detail = pd.merge(next_detail,
                price_d.loc[price_d.date==rebal_date, ['date', 'itemcode']],
                left_on=['date', 'itemcode'],
                right_on=['date', 'itemcode'], how='left')
        next_detail['username'] = self.username
        next_detail['userid'] = self.userid
        next_detail['original'] = 'Rebal'
        next_detail = next_detail.rename(columns={'weights':'wt'})
        next_detail = next_detail[['itemcode', 'quantity', 'cost_price', 'price', 'cost_value', 'value',
            'itemname', 'asset_class', 'date', 'userid', 'username', 'group_by',
            'original', 'wt']]

        return next_detail

    def run_simulation(self, first_trade=False, new_units=None, prices=None, remaining_cash=None):
        price_db = PriceDB.instance().data

        # 최근 잔고 가져오기
        # 아직 어떤 타입으로 가져오는지 모름
        detail = self.db.getUserBalance(userid=self.userid)       
        detail = pd.DataFrame(detail, columns=['date', 'userid', 'name', 'asset_class', 'itemcode', 'itemname',
                                                'quantity', 'cost_price', 'cost_value', 'price', 'value', 'wt', 'group_by', 'original'])

        # 시뮬레이션 기간은 현재일(current_date) 다음 날부터 추천 포트폴리오가 존재하는 마지막날까지임.
        dates = self.advised_pf.loc[(self.advised_pf.risk_profile == self.risk_profile) & (
            self.advised_pf.date > self.current_date), 'date'].unique()
        rebal_dates = dates[::20]
        print('리밸런싱 일자: ', rebal_dates)

        # return할 때 필요한 첫날의 추천 포트 폴리오와 asset class별 정보 수집
        df_temp = self.advised_pf.loc[(self.advised_pf.date == dates[0]) & (
            self.advised_pf.risk_profile == self.risk_profile), :]

        # first_advised_port = df_temp.copy()
        first_advised_port = df_temp.loc[:, ['weights', 'itemname']].groupby(
            'itemname').sum().reset_index()
        by_assetclass = df_temp.loc[:, ['weights', 'asset_class']].groupby(
            'asset_class').sum().sort_values('weights', ascending=False).reset_index()


        # next_detail = copy.deepcopy(detail)
        next_detail = detail
        all_the_nexts = pd.DataFrame(columns=next_detail.columns)
        nexts_list = []
        price_db = price_db.loc[:, ['date', 'price', 'itemcode']]
        for dt in dates:
#            print(dt)
            price_d = price_db.loc[price_db.date==dt, ['date', 'price', 'itemcode']]
            if dt in rebal_dates:
                # 리밸런싱한다.
                new_port = self.advised_pf.loc[(self.advised_pf.risk_profile==self.risk_profile) & (self.advised_pf.date==dt), ['date', 'itemcode', 'weights', 'itemname', 'price', 'asset_class']]
#                print('new_port.price: ', new_port[['date', 'price']])
                next_detail = self.rebalance(rebal_date=dt, price_d=price_d, detail=next_detail, new_port=new_port)
            else:
                # 리밸런싱 일자가 아니면, 새로운 종가만 업데이트하고 종목별 시가평가액(value=price*quantity)만 업데이트한다.
                next_date = datetime.strptime(dt, '%Y-%m-%d')
                #next_date = str(next_date.month)+'/'+str(next_date.day)+'/'+str(next_date.year)+' 04:00:00 PM'
                next_detail = next_detail.copy()
                next_detail['date'] = next_date
                next_detail = pd.merge(next_detail,
                                    price_d.loc[price_d.date == next_date,
                                                ['date', 'itemcode', 'price']],
                                    left_on=['date', 'itemcode'],
                                    right_on=['date', 'itemcode'],
                                    suffixes=('_cur', '_next'),
                                    how='left')
                next_detail.drop(['price_cur'], axis=1, inplace=True)
                next_detail.rename({'price_next':'price'}, axis=1, inplace=True)
                next_detail.price = next_detail.price.fillna(1)

                # 종목별 평가액과 비중 업데이트
                next_detail['value'] = next_detail['price']*next_detail['quantity']
                next_detail['wt'] = next_detail['value']/next_detail['value'].sum()
                next_detail['original'] = 'N'        
                #next_detail.loc[next_detail.itemcode=='C000001', 'price'] = 1
        #        next_detail = next_detail[['itemcode', 'quantity', 'cost_price', 'price', 'cost_value', 'value',
        #               'itemname', 'asset_class', 'date', 'userid', 'username', 'group_by',
        #               'original', 'wt']]

            # all_the_nexts = pd.concat((all_the_nexts, next_detail))
            nexts_list.append(next_detail)

        all_the_nexts = pd.concat(nexts_list, axis=0)

        print('리밸런싱 종료----')
        # 불필요한 컬럼 및 행 삭제
        all_the_nexts = all_the_nexts.loc[all_the_nexts.quantity > 0]
        all_the_nexts = all_the_nexts.reset_index(drop=True)
        all_the_nexts['username'] = self.username

        all_the_generals = all_the_nexts.loc[:,['date', 'wt', 'value', 'asset_class']].sort_values(
                                          ['date'], ascending=True).groupby([
                                              'date', 'asset_class'
                                          ]).sum().reset_index(drop=False)
        print('자산군별 요약 계산 종료----')

        all_the_generals['userid'] = self.userid

        # general 테이블 기록
        self.db.insert_general(all_the_generals)

        # detail 테이블에 기록
        self.db.insert_detail(all_the_nexts)

        print('테이블 업데이트 종료----')

        # del all_the_generals
        # del all_the_nexts

        # investor 테이블 기록
        # self.db.insert_investor(userid=self.userid, name=self.username, profile_code=self.risk_profile)
    
        return first_advised_port, by_assetclass


    def predict(self, answers, first_trade) -> object:
        # data = pd.read_pickle(os.getcwd()+'\\data\\processed\\'+self.file_name)
        data = pd.read_pickle('./data/processed/'+self.file_name)

        self.score = 0
        for idx, choice in enumerate(self.options[:-3]):
#            print(choice)
#            print(data[data['choice-id'] == choice])
            risk_value = data[data['choice-id'] == choice]['risk_pref_value'].values[0]
#            print('risk_value : ', risk_value)
            self.score += risk_value
            answers[idx] = (answers[idx], risk_value)
        # print('----------------날짜------------------')
        self.current_date = self.options[-2]  # 날짜.
        # print(self.current_date)
        self.current_date = datetime.strptime(
            self.current_date, '%Y-%m-%d').strftime('%Y-%m-%d')


        self.username = self.options[-1]

        self.userid = self.db.newUser(
            answers, money=self.options[-3], current_date=self.current_date, username=self.username)
        # print('### userid is {} #####'.format(self.userid))

        # 추천 포트폴리오를 가져온다.
        self.advised_pf = AdvisedPortfolios.instance().data
        self.risk_profile = self.score//(len(self.options)-3)

        first_advised_port, by_asset_class = self.run_simulation(first_trade=first_trade)

        return self.scoring[self.score//(len(self.options) - 3)], first_advised_port, by_asset_class, self.score//(len(self.options) - 3), datetime.strptime(self.options[-2], '%Y-%m-%d').strftime('%Y-%m-%d'), self.risk_profile
