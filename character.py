import pandas as pd
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
            print(data[data['choices'] == choice])
            risk_value = data[data['choices'] == choice]['risk_pref_value'].values[0]
            print('risk_value : ', risk_value)
            score += risk_value
            answers[idx] = (answers[idx], risk_value)
        print('----------------answer------------------')
        print(answers)
        self.db.newUser(answers, self.options[-3])


        df = pd.DataFrame(
            {
                "자산": [0, 0, 0, int(self.options[-3])],
                "종류": ['채권', '주식', '대체', '현금']
            }
        )
        return self.scoring[score//(len(self.options) - 3)], df, score

