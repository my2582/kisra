import numpy as np
import pandas as pd

import riskfolio.ConstraintsFunctions as cf
import riskfolio.Portfolio as pf
import datetime
import utils


class PortfolioAdvisor:
    r"""
    투자자 성향을 입력받아 추천 포트폴리오와 주문지를 생성한다.

    Parameters
    ----------
    risk_profile : int or float
        투자자 성향. 현재는 투자자 성향 분류 개수가 적어, 유한한 정수값으로 투자자 성향을 표현한다.
        따라서 float값이 전달되더라도, 그걸 버림한 정수값만 의미를 갖는다.
    current_date : str
        현재 날짜
    freq : str
        {'d'|'w'|'m'} 중 1개 값을 가질 수 있으나 현재는 'w'만 지원.
    """
    def __init__(self,
            risk_profile=None,
            current_date=None,
            freq='w'):
        
        self._risk_profile=risk_profile
        self.current_date=current_date
        self.freq=freq


        self.load_data()
        self.load_constraints()
    
    @property
    def risk_profile(self):
        if self._risk_profile is not None:
            return self._risk_profile
        else:
            raise NameError('risk_profile must not be None.')
    
    @risk_profile.setter
    def risk_profile(self, value):
        if value is not None:
            self._risk_profile = int(value)
        else:
            raise NameError('risk_profile must not be None.')


    def load_data(self):
        r"""
        종가, 투자가능종목, 제약조건 등 데이터를 읽어온다.
        """

        # #### Load asset classification and constraints information
        # - `asset_classes` <- `universe` <- simulatable_instruments.pkl left join with instruments_m.pkl
        # - `constraints` <- constraints.pkl

        # 가격 데이터
        # price_db.pkl
        filepath = '../../data/external/'
        filename = 'price_db_' + self.freq + '.pkl'
        self.price_db = pd.read_pickle(filepath+filename)
        print('Loaded: {}'.format(filename))

        # 읽어온 종목들의 수익률 계산
        self.calculate_internals()

        # instruments_m: 투자가능 종목들 목록 (현재 시점의 거래금액, 시총 보고 뽑음)
        filepath = '../../data/processed/'
        filename = 'instruments_m.pkl'
        self.instruments_m = pd.read_pickle(filepath+filename)
        print('Loaded: {}'.format(filename))

        # simulatable_instruments: 상장된 지 3년 넘은 종목 (시뮬레이션을 위해 필요한 요건)
        filepath = '../../data/external/'
        filename = 'simulatable_instruments.pkl'
        self.simulatable_instruments = pd.read_pickle(filepath+filename)
        print('Loaded: {}.'.format(filename))

        # 사용자가 지정한 제약조건 테이블. Aw>=B 형식으로 되어 있어 사람이 이해하기 편함.
        filepath = '../../data/processed/'
        filename = 'constraints.pkl'
        self.df_constraints = pd.read_pickle(filepath+filename)
        print('Loaded: {}.'.format(filename))

        # universe가 투자가능(예:거래량요건 충족)&시뮬레이션가능(예:상장 후 3년 종가 존재요건 충족)을 종합한 df임.
        self.universe = pd.merge(self.simulatable_instruments, self.instruments_m, left_on='itemcode', right_on='itemcode', how='left')
        self.universe = self.universe.set_index(['itemcode'], drop=True).loc[self.df_rt.columns]
        self.universe = self.universe.reset_index()

        # asset_classes는 Riskfolio 패키지가 요구하는 형식으로 고정되어 있는 투자종목들의 df임.
        self.asset_classes = utils.get_asset_classes(self.universe)

    def calculate_internals(self):
        # Make `df_rt`, a matrix of log returns of all eligible **instruments** in the universe with:
        # - Columns: itemcode
        # - Rows: date
        self.df_rt = self.price_db[self.price_db.itemtype=='ETF'].pivot(index='date', columns='itemcode', values='ret').dropna()

        print('Price returns have been calculated.')
        
    def load_constraints(self):
        self.constraints = self.df_constraints[np.logical_or(
            self.df_constraints.risk_profile == str(self._risk_profile), self.df_constraints.risk_profile == 'Common')].drop(['risk_profile'], axis=1)


        # #### We have constraints matrice `A` and `B` such that
        # - $Aw \ge B$.
        self._A, self._B = cf.assets_constraints(self.constraints, self.asset_classes)

        print('Portfolio constraints have been set in matrice A and B such that Aw>=B for a risk profile number {}.'.format(self._risk_profile))
    
    def optimize(self, drop_wt_threshold=0.005, model='Classic', rm='CDaR', method_mu='hist', method_cov='oas', decay=0.97, allow_short=False, alpha=0.05):
        r"""
        Riskfolio 패키지를 이용하여 최적화한다. Riskfolio는 내부적으로 최근 사용층을 넓혀가고 있는 cvxpy를 이용한다.
        ref: https://riskfolio-lib.readthedocs.io/en/latest/portfolio.html

        Estimaing mean risk portfolios

        - Using CDaR instead of variance as a risk measure.
          - Conditional Drawdown at Risk(CDaR) is the average drawdown for all the instances that drawdown exceeded a certain threshold.
          Drawdown is a measure of downside risk.
          - https://breakingdownfinance.com/finance-topics/alternative-investments/conditional-drawdown-at-risk-cdar/

        
        Parameters:
        파라미터 대부분 Riskfolio에 그대로 전달하므로 Riskfolio를 참고.

        alpha : float, optional
            Significance level of CVaR and CDaR. The default is 0.05.
        """        

        # `y` is a matrix of log returns of all eligible instruments in the universe.
        y = self.df_rt[self.df_rt.index <= self.current_date]

        # df_rf: 무위험 수익률 테이블
        df_rf = self.price_db[self.price_db.itemtype=='riskfree'].set_index('date', drop=True)
        current_idx = df_rf.index.asof(datetime.datetime.strptime(self.current_date, '%Y-%m-%d'))
        self.rf = df_rf.loc[current_idx].price  # rf: 현재일 기준 risk free rate
        print('The risk free rate at this time is set to be {:0.2%}'.format(self.rf))

        # Riskfolio 패키지의 Portfolio 인스턴스 생성
        # #### Set a log-return matrix `y`
        self.port = pf.Portfolio(returns=y, sht=allow_short, alpha=alpha)   # short 불가조건(sht=allow_short)

        # 최적화 제약조건 설정
        self.port.ainequality = self._A
        self.port.binequality = self._B

        # Estimate optimal portfolio:
        self.model=model # Could be Classic (historical), BL (Black Litterman) or FM (Factor Model)
        self.rm = 'CDaR'     # Risk measure used, this time will be variance
        self.obj = 'MaxRet' if self._risk_profile==4 else 'MinRisk' # Objective function, could be MinRisk, MaxRet, Utility or Sharpe


        # MVO 최적화에 필요한 기대수익률, 분산공분산 행렬 등을 계산 (model이 'Classic'으로 설정되어 있을 경우)
        if self.model == 'Classic':
            self.port.assets_stats(method_mu=method_mu, method_cov=method_cov, d=decay)

        self.w = self.port.optimization(model=self.model, rm=self.rm, obj=self.obj, rf=self.rf)
        print('Optimized weights have been estimated.')

        # threshold보다 작은 비중은 버린다(0%로 처리).
        self.drop_trivial_weights(threshold=drop_wt_threshold)
        print('Weights < {} are dropped to zero.'.format(drop_wt_threshold))

        # ETF추적지수나 종목명 정보를 종목코드에 추가해서 반환한다.
        self.add_instruments_info()

        return self.w


    def drop_trivial_weights(self, threshold=0.005):
        r"""
        threshold보다 작은 비중은 버린다(0%로 처리).
        """
        self.w.loc[np.abs(self.w.weights)<threshold,'weights'] = 0
    
    def add_instruments_info(self):
        r"""
        ETF추적지수나 종목명 정보를 종목코드에 추가해서 반환한다.
        """
        self.w = pd.merge(self.w, self.universe.loc[:,['itemcode', 'tracking_code', 'itemname']], left_index=True, right_on='itemcode', how='left')
        self.w = self.w[['weights', 'tracking_code', 'itemcode', 'itemname']].set_index('itemcode', drop=True)

    def get_it_neat(self, threshold=0.0495):
        r"""
        threshold보다 작은 비중으로 추천된 종목들의 비중을 합산하여 Others라는 이름의 비중 1개로 바꿔 df를 리턴한다.
        """
        small_wt = self.w[self.w.weights < threshold].weights.sum()
        w_others = pd.DataFrame.from_dict(
            {'OTHERS': [self.w[self.w.weights < 0.0495].weights.sum(), 'Others', 'Others']},
            orient='index',
            columns=w.columns) if small_wt >= 0.00495 else None

        return pd.concat([self.w.drop(self.w[self.w.weights<0.0495].index), w_others]).sort_values(by='weights', ascending=False)
