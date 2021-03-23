import pandas as pd
from src.models.load_data import Balance, Instruments, AdvisedPortfolios, PriceDB, Singleton
from src.models.utils import get_current_port, get_advised_port, get_recommendation
from DataBase import databaseDF
from datetime import datetime
import copy
import re
from src.models.portfolio import Portfolio

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

    def get_detail(self, new_units, prices, remaining_cash):
        # c_date: 추천 포트폴리오DB에서 사용자가 입력한 날짜와 가장 가까운 날짜.
        c_date = self.advised_pf.loc[self.advised_pf.date <= self.current_date, ['date']].max().date
        df = self.advised_pf.loc[(self.advised_pf.date==c_date) & (self.advised_pf.risk_profile==self.risk_profile), :]

        # 보유수량
        detail = pd.DataFrame.from_dict(new_units, orient='index').rename(columns={0:'quantity'})
        detail.index.name='itemcode'

        # 매입가격
        temp = pd.DataFrame.from_dict(prices, orient='index').rename(columns={0:'cost_price'}).drop([1], axis=1)
        temp.index.name='itemcode'

        # 병합
        detail = detail.merge(temp, left_index=True, right_index=True, how='inner')

        instruments_m = Instruments.instance().data
        detail['price'] = detail['cost_price']
        detail['cost_value'] = detail['quantity']*detail['cost_price']
        detail['value'] = detail['quantity']*detail['cost_price']  # 매입가와 평가가격 동일하다고 가정
        detail = detail.merge(instruments_m.loc[:, ['itemcode', 'itemname', 'asset_class']], left_on='itemcode', right_on='itemcode', how='left')
        detail = detail.reset_index(drop=True)

        # 잔액으로 현금 레코드 기록
        df_cash = {
            'itemcode': 'C000001',
            'quantity': remaining_cash,
            'cost_price': 1,
            'cost_value': remaining_cash,
            'value': remaining_cash,
            'itemname': '현금',
            'asset_class': 'Cash'
        }
        df_cash = pd.DataFrame.from_dict(df_cash, orient='index').T

        detail = pd.concat([detail, df_cash])
        detail['date'] = c_date
        detail['date'] = pd.to_datetime(detail['date'], format='%Y-%m-%d').dt.strftime('%m/%d/%Y 4:0:00 PM').astype(str)
        detail['userid'] = self.userid
        detail['username'] = self.username
        detail['group_by'] = ''
        detail['original'] = 'N'
        
        # 종목비중 구하기
        detail['wt'] = detail.value.transform(lambda x: x/x.sum())

        detail = detail.reset_index(drop=True)

        return detail

    def get_ordersheets(self):
        balance = self.db.getDetail(userid=self.userid)

        print('balance[0] is '.format(balance[0]))
        balance_date = balance[0][0]

        self.price_db = PriceDB.instance().data
        self.price_db.loc[self.price_db.date == balance_date]

        try:
            balance_date = datetime.strptime(
                balance_date, '%Y-%m-%d %H:%M:%S %p').strftime('%Y-%m-%d')
        except:
            balance_date = datetime.strptime(
                balance_date, '%m/%d/%Y %H:%M:%S %p').strftime('%Y-%m-%d')

        print('balance_date: {}'.format(balance_date))

        balance = pd.DataFrame(balance, columns=['date', 'userid', 'name', 'asset_class', 'itemcode', 'itemname', 'quantity', 'cost_price', 'cost_value', 'price', 'value', 'wt', 'group_by', 'original'])
        balance = balance.drop(['price'], axis=1)
        print('---balance---')
        print(balance)

        new_port = get_advised_port(risk_profile=self.risk_profile, df_advised_ports=self.advised_pf)

        old_new = pd.merge(balance.loc[:, ['itemcode', 'quantity', 'value', 'wt']], new_port.loc[:, ['itemcode', 'wt']],
                        left_on=['itemcode'], right_on=['itemcode'], how='outer', suffixes=['_old', '_new'])

        old_new.loc[:, ['value', 'wt_old', 'quantity', 'wt_new']] = old_new.loc[:, [
            'value', 'wt_old', 'quantity', 'wt_new']].fillna(value=0)

        assets = old_new.loc[(old_new.itemcode != 'C000001')
                            & (old_new.itemcode != 'D000001'), :]
        cash = old_new.loc[(old_new.itemcode == 'C000001') |
                        (old_new.itemcode == 'D000001'), :]
        old_assets = assets.drop(['wt_new'], axis=1)
        # old_assets = old_assets.rename(columns={'price_old':'price', 'wt_old':'wt'})
        old_cash = cash.drop(['wt_new'], axis=1)
        # old_cash = old_cash.rename(columns={'price_old':'price', 'wt_old':'wt'})
        old_tickers = assets.itemcode.tolist()
        old_quantities = assets.quantity.astype(int).tolist()
        assets = assets.merge(self.price_db.loc[self.price_db.date == balance_date, ['itemcode', 'price']],
                    left_on='itemcode', right_on='itemcode', how='left', suffixes = ('', '_db'))
        # assets.loc[:, 'price'] = assets['price'].fillna(assets['self.price_db'])

        old_prices = assets.price.tolist()
        cash_amounts = cash.value.tolist()
        cash_currency = ['KRW']*len(cash_amounts)

        p = Portfolio()
        p.easy_add_assets(tickers=old_tickers,
                        quantities=old_quantities, prices=old_prices)
        p.easy_add_cash(amounts=cash_amounts, currencies=cash_currency)
        p.selling_allowed = True

        new_tickers = old_new.loc[(old_new.itemcode != 'CASH') & (
            old_new.itemcode != 'DEPOSIT'), 'itemcode'].tolist()
        # 단위가 %이므로 100을 곱한다.
        new_wt = (old_new.loc[(old_new.itemcode != 'CASH') & (
            old_new.itemcode != 'DEPOSIT'), 'wt_new']*100).tolist()

        target_asset_alloc = dict(zip(new_tickers, new_wt))

        print('----target_asset_alloc----')
        print(target_asset_alloc)

        # p.rebalance() returns a tuple of:
        # * new_units (Dict[str, int]): Units of each asset to buy. The keys of the dictionary are the tickers of the assets.
        # * prices (Dict[str, [float, str]]): The keys of the dictionary are the tickers of the assets. Each value of the dictionary is a 2-entry list. The first entry is the price of the asset during the rebalancing computation. The second entry is the currency of the asset.
        # * remaining_cash (float): The remaining cash after rebalancing.
        # * max_diff (float): Largest difference between target allocation and optimized asset allocation.
        (new_units, prices, remaining_cash, max_diff) = p.rebalance(target_asset_alloc, verbose=True)

        # 리밸런싱을 실행하기 위한 주문내역을 detail 테이블에 넣기 위하여 df 로 받음.
        new_detail = self.get_detail(new_units, prices, remaining_cash)

        # detail 테이블에 기록
        self.db.insert_detail(new_detail)

        return (new_units, prices, remaining_cash)

    def predict(self, answers) -> object:
        # data = pd.read_pickle(os.getcwd()+'\\data\\processed\\'+self.file_name)
        data = pd.read_pickle('./data/processed/'+self.file_name)

        self.score = 0
        for idx, choice in enumerate(self.options[:-3]):
            print(choice)
            print(data[data['choice-id'] == choice])
            risk_value = data[data['choice-id'] == choice]['risk_pref_value'].values[0]
            print('risk_value : ', risk_value)
            self.score += risk_value
            answers[idx] = (answers[idx], risk_value)
        print('----------------answer------------------')
        print(answers)
        self.db.newUser(answers, self.options[-3])


        # 추천 포트폴리오를 가져온다.
        self.advised_pf = AdvisedPortfolios.instance().data
        self.risk_profile = self.score//(len(self.options)-3)
        self.current_date = self.options[-2]  # 날짜.
        self.current_date = datetime.strptime(self.current_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        
        self.username = self.options[-1]
        # 사용자명에서 숫자만 갖고온다. 그래서 A+숫자 형식의 userid를 만든다.
        self.userid = 'A' + ('0'+re.findall('\d+', self.username)[0])[-2:] 

        def simulate_trades(self, first_trade=False, new_units=None, prices=None, remaining_cash=None):
            if first_trade:
                # 추천 포트폴리오DB에서 사용자가 입력한 날짜와 가장 가까운 날짜.
                self.current_date = self.advised_pf.loc[self.advised_pf.date <= self.current_date, ['date']].max().date
                print('The date we are looking for is {}'.format(self.current_date))
                df = self.advised_pf.loc[(self.advised_pf.date==self.current_date) & (self.advised_pf.risk_profile==self.risk_profile), :]

                first_advised_port = copy.deepcopy(df)
                first_advised_port = first_advised_port.loc[:, ['weights', 'itemname']].groupby(
                        'itemname').sum().reset_index()
        
                print('self.options is {}'.format(self.options))
                print('첫 추천포트폴리오(risk profile {}):'.format(self.risk_profile))
                print(first_advised_port)

                new_units, prices, remaining_cash = self.get_ordersheets()
                print('---new_units---')
                print(new_units)
                print('---prices----')
                print(prices)

                return first_advised_port, new_units, prices, remaining_cash
            else:
                dates = advised_pf.loc[(advised_pf.risk_profile==risk_profile) & (advised_pf.date > current_date), 'date'].unique()
                every5day = dates[::5]
                for dt in dates:
                    balance = self.db.getDetail(userid=self.userid)
                    balance_date = balance[0][0]
                    print('dt {}, balance_date {}-type(balance):'.format(dt, balance_date, type(balance)))
                    print(balance)
                    try:
                        balance_date = datetime.strptime(
                            balance_date, '%Y-%m-%d %H:%M:%S %p').strftime('%Y-%m-%d')
                    except:
                        balance_date = datetime.strptime(
                            balance_date, '%m/%d/%Y %H:%M:%S %p').strftime('%Y-%m-%d')

                    if dt is every5day:
                        # 추천 포트폴리리와 현재 포트폴리오 비중차가 5% 넘게 나는 종목이 생기면 리밸런싱 (그러면 종가도 업데이트되는 셈)
                        pass
                    else:
                        # 종가만 업데이트
                        pass

            return new_units, prices, remaining_cash


        first_advised_port, new_units, prices, remaining_cash = simulate_trades(first_trade=True)
        simulate_trades(first_trade=False, new_units=new_units, prices=prices, remaining_cash=remaining_cash)

        return self.scoring[self.score//(len(self.options) - 3)], first_advised_port, self.score//(len(self.options) - 3), new_units, prices, remaining_cash 

