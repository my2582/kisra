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
            self.advised_pf.date >= self.current_date), 'date'].unique()
        rebal_dates = dates[::30]
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
            risk_value = data[data['choice-id'] == choice]['risk_pref_value'].values[0]
            self.score += risk_value
            answers[idx] = (answers[idx], risk_value)

        self.current_date = self.options[-2]  # 날짜.
        # print(self.current_date)
        self.current_date = datetime.strptime(
            self.current_date, '%Y-%m-%d').strftime('%Y-%m-%d')



        # 추천 포트폴리오를 가져온다.
        self.advised_pf = AdvisedPortfolios.instance().data
        self.risk_profile = self.score//(len(self.options)-3)

        self.username = self.options[-1]

        self.userid = self.db.newUser(
            answers, money=self.options[-3], current_date=self.current_date, username=self.username, risk_profile=self.risk_profile)
        # print('### userid is {} #####'.format(self.userid))


        first_advised_port, by_asset_class = self.run_simulation(first_trade=first_trade)

        return self.scoring[self.score//(len(self.options) - 3)], first_advised_port, by_asset_class, self.score//(len(self.options) - 3), datetime.strptime(self.options[-2], '%Y-%m-%d').strftime('%Y-%m-%d'), self.risk_profile
