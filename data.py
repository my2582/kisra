import pandas as pd
from DataBase import databaseDF
from datetime import date as dt
from src.models.load_data import AdvisedPortfolios, Singleton

class Data:
    def __init__(self):
        # self.pre_data = pd.read_pickle(os.getcwd()+'\\data\\processed\\balance_m.pkl')
        # self.detail_data = pd.read_pickle(os.getcwd()+'\\data\\processed\\balance_s.pkl')
        self.usersel = pd.read_pickle('./data/processed/profiles_s.pkl')
        self.pre_data = pd.read_pickle('./data/processed/balance_m.pkl')
        self.detail_data = pd.read_pickle('./data/processed/balance_s.pkl')
        self.investors_m =  pd.read_pickle('./data/processed/investors_m.pkl')
        self.advised_pf = AdvisedPortfolios.instance().data
        self.columns = list(self.detail_data.columns)
        self.db = databaseDF()
        print('Data is initialized -------------------. detailed_data is')
        self.db.createDefault((self.pre_data, self.detail_data, self.usersel, self.investors_m))
        print(self.detail_data)
        
        #self.detail_data = pd.read_pickle('./data/processed/balance_s.pkl')
        #self.detail_data = pd.read_pickle('./data/processed/balance_s.pkl') 

    def uniqueUser(self, return_pd=False):
        #users = self.detail_data['name'].tolist()
        users = self.db.getUserList()
        users = pd.DataFrame(users, columns=['userid', 'name'])

        if return_pd:
            # DataFrame 형식으로 리턴
            return users

        # 이름만 리스트로 리턴
        return list(set(users.name))

    def getUserId(self, name):
        df_users = self.uniqueUser(return_pd=True)
        userid = df_users.loc[df_users.name==name, 'userid'].iloc[0]
        return userid

    def specificDate(self, name):
        print('------------------in specificDate() name------------------------------')
        print(name)
        date = self.db.getMaxDate(name)
        return date[-1][0]

    def getRiskProfile(self, name):
        profile_code = self.db.getUserRiskProfile(name)
        return profile_code

    def getUserBalance(self, name):
        userid = self.check_name(name)
        self.balance = self.db.getUserBalance(userid)

        return self.balance

    def defaults(self):
        background = self.detail_data[self.detail_data[self.columns[-1]] == 'Y']
        date = background[self.columns[0]].iloc[0]
        name = background[self.columns[2]].iloc[0]
        userid = background[self.columns[1]].iloc[0]
        print('---in defaults(): date={} / name={}'.format(date, name))
        return name, date, userid

    def check_name(self, name):
        try:
            #user_id = self.detail_data[self.detail_data['name'] == name]['userid'].iloc[0]
            user_id = self.getUserId(name)
            return user_id
        except:
            return False

    def getSelection(self, name):
        print(name)
        userid = self.check_name(name)
        print(userid)
        return self.db.getSelection(userid)

    def returnPage3Data(self, name, date):
        user_id = self.check_name(name)

        if not user_id:
            return '존재하지 않는 사용자입니다. 가입 먼저 해주세요'

        baseline = self.detail_data[self.detail_data[self.columns[2]] == name]
        standard_date = self.db.getDate(user_id, date)
        print('standard_date : ', standard_date)
        answer = self.pre_data[(self.pre_data['date'] == standard_date)&(self.pre_data['userid'] == user_id)]

        return answer, baseline[baseline[self.columns[0]] == standard_date]

    def returnData(self, point, name=None, date=None, choice=False):
        if name is None:
            name = '투자자1'
            date='3/22/2021 4:00:00 PM'

        user_id = self.check_name(name)

        if not user_id:
            return '존재하지 않는 사용자입니다. 가입 먼저 해주세요'
        # commented on 4/24 at 12:38PM ----------------
        # data = self.pre_data[self.pre_data['userid'] == user_id]

        # start, end = point
        # standard_date = dt.today().strftime('%m/%d/%y')+' 1:00:00 AM'

        # if choice:
        #     data = self.db.getRecord(user_id, (standard_date, start, end))
        #     if not len(data):
        #         return pd.DataFrame(columns=self.columns)
        #     data.columns = self.columns
        #     return data
        #
        # return data[data['date'] == date], data[data['date'] == date]
        # -------------------------------------------

        start, end = point
        standard_date = dt.today().strftime('%m/%d/%y')+' 1:00:00 AM'

        data = self.db.getRecord(user_id, (standard_date, start, end))
        if not len(data):
            return pd.DataFrame(columns=self.columns)
        data.columns = self.columns
        return data
