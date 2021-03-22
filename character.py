import pandas as pd
from src.models.load_data import Balance, Instruments, AdvisedPortfolios, PriceDB, Singleton
from DataBase import databaseDF
from datetime import datetime

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
        current_date = self.options[-2]  # 날짜.
        current_date = datetime.strptime(current_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        df = advised_pf.loc[(advised_pf.date==current_date) & (advised_pf.risk_profile==score), :]
        df.loc[:, ['weights', 'asset_class']].groupby(
            'asset_class').sum().reset_index().rename(columns={
                'asset_class': '자산군',
                'weights': '비중'
            })
        
        print('self.options is {}'.format(self.options))
        print('추천포트폴리오:')
        print(df)

        # df = pd.DataFrame(
        #     {
        #         "자산": [0, 0, 0, int(self.options[-3])],
        #         "종류": ['채권', '주식', '대체', '현금']
        #     }
        # )
        return self.scoring[score//(len(self.options) - 3)], df, score//(len(self.options) - 3)

