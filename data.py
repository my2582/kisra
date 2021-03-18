import pandas as pd
from DataBase import databaseDF

class Data:
    def __init__(self):
        # self.pre_data = pd.read_pickle(os.getcwd()+'\\data\\processed\\balance_m.pkl')
        # self.detail_data = pd.read_pickle(os.getcwd()+'\\data\\processed\\balance_s.pkl')
        self.usersel = pd.read_pickle('./data/processed/profiles_s.pkl')
        self.pre_data = pd.read_pickle('./data/processed/balance_m.pkl')
        self.detail_data = pd.read_pickle('./data/processed/balance_s.pkl')
        self.columns = list(self.detail_data.columns)
        self.db = databaseDF()

    def uniqueUser(self):
        users = self.detail_data['name'].tolist()
        return list(set(users))

    def specificDate(self, name):
        return self.detail_data[(self.detail_data[self.columns[-1]] == 'Y') & (self.detail_data[self.columns[2]] == name)]['date'].iloc[0]

    def defaults(self):
        background = self.detail_data[self.detail_data[self.columns[-1]] == 'Y']
        date = background[self.columns[0]].iloc[0]
        name = background[self.columns[2]].iloc[0]
        return name, date

    def check_name(self, name):
        try:
            user_id = self.detail_data[self.detail_data['name'] == name]['userid'].iloc[0]
            return user_id
        except:
            return False

    def returnPage3Data(self, name, date):
        user_id = self.check_name(name)

        if not user_id:
            return '존재하지 않는 사용자입니다. 가입 먼저 해주세요'

        baseline = self.detail_data[self.detail_data[self.columns[2]] == name]
        standard_date = self.db.getDate(user_id, date)

        answer = self.pre_data[(self.pre_data['date'] == standard_date)&(self.pre_data['userid'] == user_id)]

        return answer, baseline[baseline[self.columns[0]] == standard_date]

    def returnData(self, point, name, date, choice=False):
        user_id = self.check_name(name)

        if not user_id:
            return '존재하지 않는 사용자입니다. 가입 먼저 해주세요'

        data = self.pre_data[self.pre_data['userid'] == user_id]

        start, end = point
        standard_date = date.today().strftime('%m/%d/%y')+' 0:00:00 AM'

        if choice:
            data = self.db.getRecord(user_id, (standard_date, start, end))
            data.columns = self.columns
            return data

        return data[data['date'] == date], data[data['date'] == date]