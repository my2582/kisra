import pandas as pd
from src.models.load_data import Balance, Instruments, AdvisedPortfolios, PriceDB, Singleton
from src.models.utils import get_current_port, get_advised_port, get_recommendation
from DataBase import databaseDF
from datetime import datetime
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

    def get_ordersheets(self, advised_pf, username, userid, current_date, risk_profile):
        balance = self.db.getDetail(userid=userid)

        print('balance[0] is '.format(balance[0]))
        balance_date = balance[0][0]

        price_db = PriceDB.instance().data
        price_db.loc[price_db.date == balance_date]

        print('----price_db-----')
        print(price_db.tail())

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

        new_port = get_advised_port(risk_profile=risk_profile, df_advised_ports=advised_pf)
        print('new_port.price')
        print(new_port.price)
        print('advised_pf.price')
        print(advised_pf.price)

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
        assets = assets.merge(price_db.loc[price_db.date == balance_date, ['itemcode', 'price']],
                    left_on='itemcode', right_on='itemcode', how='left', suffixes = ('', '_db'))
        # assets.loc[:, 'price'] = assets['price'].fillna(assets['price_db'])
        print('---assets---')
        print(assets)

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

        print('---new_port---')
        print(new_port)

        print('---old_new---')
        print(old_new)

        print('----target_asset_alloc----')
        print(target_asset_alloc)

        # p.rebalance() returns a tuple of:
        # * new_units (Dict[str, int]): Units of each asset to buy. The keys of the dictionary are the tickers of the assets.
        # * prices (Dict[str, [float, str]]): The keys of the dictionary are the tickers of the assets. Each value of the dictionary is a 2-entry list. The first entry is the price of the asset during the rebalancing computation. The second entry is the currency of the asset.
        # * exchange_rates (Dict[str, float]): The keys of the dictionary are currencies. Each value is the exchange rate to CAD during the rebalancing computation.
        # * max_diff (float): Largest difference between target allocation and optimized asset allocation.
        (new_units, prices, _, max_diff) = p.rebalance(target_asset_alloc, verbose=True)

        return (new_units, prices)


    def predict(self, answers) -> object:
        # data = pd.read_pickle(os.getcwd()+'\\data\\processed\\'+self.file_name)
        data = pd.read_pickle('./data/processed/'+self.file_name)

        score = 0
        for idx, choice in enumerate(self.options[:-3]):
            print(choice)
            print(data[data['choice-id'] == choice])
            risk_value = data[data['choice-id'] == choice]['risk_pref_value'].values[0]
            print('risk_value : ', risk_value)
            score += risk_value
            answers[idx] = (answers[idx], risk_value)
        print('----------------answer------------------')
        print(answers)
        self.db.newUser(answers, self.options[-3])

        # 추천 포트폴리오를 가져온다.
        advised_pf = AdvisedPortfolios.instance().data
        risk_profile = score//(len(self.options)-3)
        current_date = self.options[-2]  # 날짜.
        current_date = datetime.strptime(current_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        
        username = self.options[-1]
        # 사용자명에서 숫자만 갖고온다. 그래서 A+숫자 형식의 userid를 만든다.
        userid = 'A' + ('0'+re.findall('\d+', username)[0])[-2:] 

        # c_date: 추천 포트폴리오DB에서 사용자가 입력한 날짜와 가장 가까운 날짜.
        current_date = advised_pf.loc[advised_pf.date <= current_date, ['date']].max().date
        print('The date we are looking for is {}'.format(current_date))
        df = advised_pf.loc[(advised_pf.date==current_date) & (advised_pf.risk_profile==risk_profile), :]
        # df = df.loc[:, ['weights', 'itemname']].groupby(
        #         'itemname').sum().reset_index().rename(columns={
        #         'itemname': 'Name',
        #         'weights': 'Weight'
        #     })
        
        print('self.options is {}'.format(self.options))
        print('추천포트폴리오(risk profile {}):'.format(risk_profile))
        print(df)

        new_units, prices = self.get_ordersheets(advised_pf, username, userid, current_date, risk_profile)
        print('---new_units---')
        print(new_units)
        print('---prices----')
        print(prices)

        

        return self.scoring[score//(len(self.options) - 3)], df, score//(len(self.options) - 3)

