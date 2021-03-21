import numpy as np
import pandas as pd

import riskfolio.ConstraintsFunctions as cf
import riskfolio.Portfolio as pf
import datetime

if __name__ == '__main__':
    from utils import get_asset_classes
    from asset import Asset
    from price import Price
    from load_data import Singleton, Balance, Instruments, PriceDB, SimulatableInstruments, Constraints, AdvisedPortfolios
else:
    from .utils import get_asset_classes
    from .asset import Asset
    from .price import Price
    from .load_data import Singleton, Balance, Instruments, PriceDB, SimulatableInstruments, Constraints, AdvisedPortfolios


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
    w : DataFrame
        추천된 포트폴리오 정보. self._optimize()가 실행될 때마다 이 값이 갱신된다.
        컬럼: 종목코드(itemcode)가 인덱스이고, 비중(weights), 추적지수코드(tracking_code), 종목명(itemname)
    weights : DataFrame
        추천된 포트폴리오 정보인 self.w가 성향(risk_profile), 날짜별마다 저장되는 거대한 DataFrame이다.
    """

    def __init__(self,
                 risk_profile=None,
                 current_date=None,
                 freq='w',
                 root_path='./'):

        self._risk_profile = risk_profile
        self.current_date = current_date
        self.freq = freq
        self.df_rt = None
        self.w = None
        self.weights = None
        self.root_path = root_path

    def run(self, risk_profile=None, current_date=None, non_tradables=None, drop_wt_threshold=0.005,
            model='Classic', rm='CDaR', method_mu='hist', method_cov='oas',
            decay=0.97, allow_short=False, alpha=0.05):
        r"""
        최적화 모델을 실행한다(즉, 최적화를 한다).
        risk_profile과 current_date값을 바꿔가면서 반복적으로 실행하면 self.weights에 추천 포트폴리오가 누적되어 저장된다.
        """
        self._risk_profile = risk_profile
        self.current_date = current_date
        self.non_tradables = non_tradables

        self._load_data()
        self._load_constraints()

        self.w = self._optimize(drop_wt_threshold=drop_wt_threshold, model=model, rm=rm,
                                method_mu=method_mu, method_cov=method_cov, decay=decay,
                                allow_short=allow_short, alpha=alpha)

        if self.weights is None:
            # run()이 처음으로 실행됐을 경우에는 'date', 'risk_profile' 컬럼의 빈 DataFrame을 만들어
            # 결과값인 self.w값과 결합(concat)한다.
            temp = pd.DataFrame(index=range(self.w.index.shape[0]), columns=[
                                'date', 'risk_profile'])
            temp['date'] = self.current_date
            temp['risk_profile'] = self._risk_profile

            self.weights = pd.concat([temp, self.w.reset_index()], axis=1)
            self.weights = self.weights.merge(self.price_db.loc[self.price_db.date == self.current_date].drop(
                ['date', 'ret', 'itemtype'], axis=1), left_on='itemcode', right_on='itemcode', how='left')
            self.weights = self.weights.merge(self.instruments_m.loc[:, [
                                              'itemcode', 'asset_class']], left_on='itemcode', right_on='itemcode', how='left')

        else:
            temp = self.w.copy()
            temp['date'] = self.current_date
            temp['risk_profile'] = self._risk_profile

            temp = temp.merge(self.price_db.loc[self.price_db.date == self.current_date].drop(
                ['date', 'ret', 'itemtype'], axis=1), left_on='itemcode', right_on='itemcode', how='left')
            temp = temp.merge(self.instruments_m.loc[:, [
                              'itemcode', 'asset_class']], left_on='itemcode', right_on='itemcode', how='left')
            self.weights = pd.concat(
                [self.weights, temp.reset_index(drop=True)])
            self.weights = self.weights.reset_index(drop=True)

        print('Completed optimization for {} on {}'.format(
            self._risk_profile, self.current_date))

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

    def _load_data(self):
        r"""
        종가, 투자가능종목, 제약조건 등 데이터를 읽어온다.
        """

        # #### Load asset classification and constraints information
        # - `asset_classes` <- `universe` <- simulatable_instruments.pkl left join with instruments_m.pkl
        # - `constraints` <- constraints.pkl

        # 가격 데이터
        # price_db.pkl
        # filepath = self.root_path + 'data/external/'
        # filename = 'price_db_' + self.freq + '.pkl'
        # self.price_db = pd.read_pickle(filepath+filename)
        self.price_db = PriceDB.instance().data
        self.price_db = self.price_db[~self.price_db.itemcode.isin(
            self.non_tradables)] if self.non_tradables is not None else self.price_db
        print('Loaded: PriceDB')

        # 읽어온 종목들의 수익률 계산
        self._calculate_internals()

        # instruments_m: 투자가능 종목들 목록 (현재 시점의 거래금액, 시총 보고 뽑음)
        # filepath = self.root_path + 'data/processed/'
        # filename = 'instruments_m.pkl'
        # self.instruments_m = pd.read_pickle(filepath+filename)
        self.instruments_m = Instruments.instance().data
        self.instruments_m = self.instruments_m[~self.instruments_m.itemcode.isin(
            self.non_tradables)] if self.non_tradables is not None else self.instruments_m
        self.instruments_m = self.instruments_m.reset_index(drop=True)
        print('Loaded: Instruments')

        # simulatable_instruments: 상장된 지 3년 넘은 종목 (시뮬레이션을 위해 필요한 요건)
        # filepath = self.root_path + 'data/external/'
        # filename = 'simulatable_instruments.pkl'
        # self.simulatable_instruments = pd.read_pickle(filepath+filename)
        self.simulatable_instruments = SimulatableInstruments.instance().data
        self.simulatable_instruments = self.simulatable_instruments[~self.simulatable_instruments.itemcode.isin(
            self.non_tradables)] if self.non_tradables is not None else self.simulatable_instruments
        self.simulatable_instruments = self.simulatable_instruments.reset_index(
            drop=True)
        print('Loaded: SimulatableInstruments')

        # 사용자가 지정한 제약조건 테이블. Aw>=B 형식으로 되어 있어 사람이 이해하기 편함.
        # filepath = self.root_path + 'data/processed/'
        # filename = 'constraints.pkl'
        # self.df_constraints = pd.read_pickle(filepath+filename)
        self.df_constraints = Constraints.instance().data
        print('Loaded: Constraints')

        # universe가 투자가능(예:거래량요건 충족)&시뮬레이션가능(예:상장 후 3년 종가 존재요건 충족)을 종합한 df임.
        self.universe = pd.merge(self.simulatable_instruments, self.instruments_m,
                                 left_on='itemcode', right_on='itemcode', how='left')
        self.universe = self.universe.set_index(
            ['itemcode'], drop=True).loc[self.df_rt.columns]
        self.universe = self.universe.reset_index()

        # 동일 추적지수를 갖는 ETF에서는 거래량 1위만 선정
        most_liquid_names = self.universe.loc[:, ['itemcode', 'itemname', 'tracking_code', 'trading_amt_mln']].groupby(
            ['tracking_code'])[['itemcode', 'itemname', 'trading_amt_mln']].max().itemcode
        self.universe.set_index('itemcode', drop=True).loc[most_liquid_names]

        # self.non_tradables: 거래불가 종목은 제외시킨다(예: 잔고가 100만원 이하일 경우 가격이 높은 ETF는 포트폴리오 내에서 1주 사기도 어려워 제외)
        self.universe = self.universe[~self.universe.itemcode.isin(
            self.non_tradables)] if self.non_tradables is not None else self.universe
        self.universe = self.universe.reset_index(drop=True)

        # asset_classes는 Riskfolio 패키지가 요구하는 형식으로 고정되어 있는 투자종목들의 df임.
        self.asset_classes = get_asset_classes(self.universe)

    def _calculate_internals(self):
        # Make `df_rt`, a matrix of log returns of all eligible **instruments** in the universe with:
        # - Columns: itemcode
        # - Rows: date
        self.df_rt = self.price_db[self.price_db.itemtype == 'ETF'].pivot(
            index='date', columns='itemcode', values='ret').dropna()
        print('Price returns have been calculated.')

    def _load_constraints(self):
        self.constraints = self.df_constraints[np.logical_or(
            self.df_constraints.risk_profile == str(self._risk_profile), self.df_constraints.risk_profile == 'Common')].drop(['risk_profile'], axis=1)

        # #### We have constraints matrice `A` and `B` such that
        # - $Aw \ge B$.
        self._A, self._B = cf.assets_constraints(
            self.constraints, self.asset_classes)

        print('Portfolio constraints have been set in matrice A and B such that Aw>=B for a risk profile number {}.'.format(
            self._risk_profile))

    def _optimize(self, drop_wt_threshold=0.005, model='Classic', rm='CDaR', method_mu='hist', method_cov='oas', decay=0.97, allow_short=False, alpha=0.05):
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
        df_rf = self.price_db[self.price_db.itemtype ==
                              'riskfree'].set_index('date', drop=True)
        current_idx = df_rf.index.asof(
            datetime.datetime.strptime(self.current_date, '%Y-%m-%d'))
        self.rf = df_rf.loc[current_idx].price  # rf: 현재일 기준 risk free rate
        print(
            'The risk free rate at this time is set to be {:0.2%}'.format(self.rf))

        # Riskfolio 패키지의 Portfolio 인스턴스 생성
        # #### Set a log-return matrix `y`
        # short 불가조건(sht=allow_short)
        self.port = pf.Portfolio(returns=y, sht=allow_short, alpha=alpha)

        # 최적화 제약조건 설정
        self.port.ainequality = self._A
        self.port.binequality = self._B

        # Estimate optimal portfolio:
        # Could be Classic (historical), BL (Black Litterman) or FM (Factor Model)
        self.model = model
        self.rm = 'CDaR'     # Risk measure used, this time will be variance
        # Objective function, could be MinRisk, MaxRet, Utility or Sharpe
        self.obj = 'MaxRet' if self._risk_profile == 4 else 'MinRisk'

        # MVO 최적화에 필요한 기대수익률, 분산공분산 행렬 등을 계산 (model이 'Classic'으로 설정되어 있을 경우)
        if self.model == 'Classic':
            self.port.assets_stats(method_mu=method_mu,
                                   method_cov=method_cov, d=decay)

        self.w = self.port.optimization(
            model=self.model, rm=self.rm, obj=self.obj, rf=self.rf)
        assert self.w is not None, "Optimization failed with these actual inputs: "
        print('Optimized weights have been estimated.')

        # threshold보다 작은 비중을 추천받은 종목은 삭제한다.
        self.drop_trivial_weights(threshold=drop_wt_threshold, drop=True)
        print('Weights < {} are dropped.'.format(drop_wt_threshold))

        # ETF추적지수나 종목명 정보를 종목코드에 추가해서 반환한다.
        self.add_instruments_info()
        self.w = self.w.sort_values(by='weights', ascending=False)

        return self.w

    def drop_trivial_weights(self, threshold=0.005, drop=True):
        r"""
        threshold보다 작은 비중은 버린다.

        Parameters
        ----------
        drop : boolean
            True면 threshold값보다 추천 비중이 작은 종목을 삭제한다.
            False면 0%로 설정하고 삭제하지는 않는다.
        """
        if drop:
            self.w = self.w.drop(
                self.w.loc[np.abs(self.w.weights) < 0.005, 'weights'].index)
        else:
            self.w.loc[np.abs(self.w.weights) < threshold, 'weights'] = 0

    def add_instruments_info(self):
        r"""
        ETF추적지수나 종목명 정보를 종목코드에 추가해서 반환한다.
        """
        self.w = pd.merge(self.w, self.universe.loc[:, [
                          'itemcode', 'tracking_code', 'itemname']], left_index=True, right_on='itemcode', how='left')
        self.w = self.w[['weights', 'tracking_code', 'itemcode',
                         'itemname']].set_index('itemcode', drop=True)

    def get_it_neat(self, threshold=0.0495):
        r"""
        threshold보다 작은 비중으로 추천된 종목들의 비중을 합산하여 Others라는 이름의 비중 1개로 바꿔 df를 리턴한다.
        """
        small_wt = self.w[self.w.weights < threshold].weights.sum()
        w_others = pd.DataFrame.from_dict(
            {'OTHERS': [self.w[self.w.weights < 0.0495].weights.sum(),
                        'Others', 'Others']},
            orient='index',
            columns=self.w.columns) if small_wt >= 0.00495 else None

        return pd.concat([self.w.drop(self.w[self.w.weights < 0.0495].index), w_others]).sort_values(by='weights', ascending=False)


if __name__ == '__main__':
    pa = PortfolioAdvisor()
    pa.run(risk_profile=2, current_date='2021-02-08')
    pa.run(risk_profile=2, current_date='2021-02-15')
    print(pa.w)
