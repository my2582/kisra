import os
import pandas as pd
from datetime import timedelta, datetime

class Data:
    def __init__(self):
        self.pre_data = pd.read_pickle(os.getcwd()+'\\data\\processed\\balance_m.pkl')
        self.detail_data = pd.read_pickle(os.getcwd()+'\\data\\processed\\balance_s.pkl')
        self.columns = list(self.detail_data.columns)

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

    def changeData(self):
        for i in range(len(self.detail_data)):
            self.detail_data.loc[i, 'date'] = datetime.strptime(self.detail_data.loc[i, 'date'], '%Y-%m-%d %H:%M:%S')

    def returnData(self, point, name, date, choice=False):
        user_id = self.check_name(name)

        if not user_id:
            return '존재하지 않는 사용자입니다. 가입 먼저 해주세요'

        data = self.pre_data[self.pre_data['userid'] == user_id]

        start, end = point
        standard_date = datetime.today()
        start = timedelta(start)
        end = timedelta(end)

        if choice:
            if type(self.detail_data.loc[0, 'date']) == str:
                self.changeData()
            data = self.detail_data[(self.detail_data['userid'] == user_id) & (self.detail_data['date'] <= standard_date-end) &
                                    (standard_date-start <= self.detail_data['date'])]
            return data

        return data[data['date'] == date], data[data['date'] == date]