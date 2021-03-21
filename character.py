import pandas as pd
from src.models.load_data import Balance, Instruments, AdvisedPortfolios, PriceDB, Singleton
from DataBase import databaseDF

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
        df = advised_pf.loc[(advised_pf.risk_profile==score) & (advised_pf.date==self.options[1])]
        df.loc[:, ['weights', 'asset_class']].groupby(
            'asset_class').sum().reset_index().rename(columns={
                'asset_class': '자산군',
                'weights': '비중'
            })

        # df = pd.DataFrame(
        #     {
        #         "자산": [0, 0, 0, int(self.options[-3])],
        #         "종류": ['채권', '주식', '대체', '현금']
        #     }
        # )
        return self.scoring[score//(len(self.options) - 3)], df, score//(len(self.options) - 3)

