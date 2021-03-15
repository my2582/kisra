import pandas as pd

pa = PortfolioAdvisor(root_path='../../')

# start_date = '2018-01-01'
# end_date = '2021-02-28'

for date in pd.bdate_range(start=start_date, end=end_date):
    for r in [2,3,4]:
        pa.run(risk_profile=r, current_date=date.strftime('%Y-%m-%d'))
