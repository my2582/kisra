import pandas as pd

import repackage
repackage.up()

from models.portfolio_advisor import PortfolioAdvisor


pa = PortfolioAdvisor(root_path='../../')
path_to_save = './data/processed/'
filename = 'advised_portfolios.pkl'

start_date = '2020-02-01'
end_date = '2020-02-28'

for date in pd.bdate_range(start=start_date, end=end_date):
    for r in [2,3,4]:
        non_tradables = None
        pa.run(risk_profile=r, current_date=date.strftime('%Y-%m-%d'), non_tradables=non_tradables)

assert pa.weights.weights.max() <= 0.25+10e-5, '[경고] 투자비중이 25% 이상인 경우 발생.'
assert all(pa.weights.loc[:, ['itemcode', 'date', 'risk_profile']].groupby(by=['date', 'risk_profile']).count().min() >= 5), '[경고] 추천종목 개수가 5개보다 적은 경우 발생.'

pa.weights.to_pickle(path_to_save+filename)

print('Saved in {}{}.'.format(path_to_save, filename))
