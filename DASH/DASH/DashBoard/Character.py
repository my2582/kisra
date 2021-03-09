import ReadWrite
import pandas as pd


class Character:
    def __init__(self, characters):
        self.file = ReadWrite.ReadWrite()
        self.options = characters
        self.file_name = 'profiles_m'
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

    def predict(self):
        data = pd.read_pickle(self.file.returnData(self.file_name))
        score = 0
        for choice in self.options[:-3]:
            score += data[data['choice-id'] == choice]['risk_pref_value'].iloc[0]
        score = score//(len(self.options) - 3)

        df = pd.DataFrame(
            {
                "자산": [0, 0, 0, int(self.options[-3])],
                "종류": ['채권', '주식', '대체', '현금']
            }
        )
        return self.scoring[score], df

