import pandas as pd
from datetime import timedelta, datetime

class Data:
    def __init__(self):
        # self.pre_data = pd.read_pickle(os.getcwd()+'\\data\\processed\\balance_m.pkl')
        # self.detail_data = pd.read_pickle(os.getcwd()+'\\data\\processed\\balance_s.pkl')
        self.pre_data = pd.read_pickle('./data/processed/balance_m.pkl')
        self.detail_data = pd.read_pickle('./data/processed/balance_s.pkl')
        self.columns = list(self.detail_data.columns)

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

    def changeSingleData(self, data):
        if type(data) == str:
            try:
                dt = datetime.strptime(data, '%Y-%m-%d %H:%M:%S').date()
            except:
                dt = datetime.strptime(data, '%m/%d/%Y %H:%M:%S %p').date()
            return dt
        return data

    def changeData(self):
        for i in range(len(self.detail_data)):
            try:
                dt = datetime.strptime(self.detail_data.loc[i, 'date'], '%Y-%m-%d %H:%M:%S %p')
            except: 
                dt = datetime.strptime(self.detail_data.loc[i, 'date'], '%m/%d/%Y %H:%M:%S %p')

            self.detail_data.loc[i, 'date'] = dt

    def unchangeData(self, data):
        for i in range(len(data)):
            try:
                dt = datetime.strftime(data.loc[i, self.columns[0]], '%Y-%m-%d %H:%M:%S %p')
            except:
                dt = datetime.strftime(data.loc[i, self.columns[0]], '%m/%d/%Y %H:%M:%S %p')
            data.loc[i, self.columns[0]] = dt
        return data

    def returnPage3Data(self, name, date):
        user_id = self.check_name(name)
        baseline = self.detail_data[self.detail_data[self.columns[2]] == name]
        standard_date = ''
        if type(baseline.loc[0, self.columns[0]])!=str:
            baseline = self.unchangeData(baseline)

        for i in range(len(baseline)):
            if baseline.loc[i, self.columns[0]] <= date:
                standard_date = baseline.loc[i, self.columns[0]]
            if date < baseline.loc[i, self.columns[0]]:
                break

        answer = self.pre_data[(self.pre_data['date'] == standard_date)&(self.pre_data['userid'] == user_id)]

        if not len(answer):
            temp = standard_date[:10]
            temp = temp.split('-')
            temp = str(int(temp[1]))+'/'+str(int(temp[2]))+'/'+temp[0]+' '+str(int(standard_date[11:13]))+standard_date[13:]
            answer = self.pre_data[(self.pre_data['date'] == temp) & (self.pre_data['userid'] == user_id)]

        return answer, baseline[baseline[self.columns[0]] == standard_date]

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