from data import Data


class User:
    def __init__(self):
        self.data = Data()
        self.name, self.date, self.userid = self.data.defaults()

    def getStartDate(self, name):
        dt = self.data.specificDate(name)
        # print('---in getStartDate(), last record for {} is {}'.format(name, dt))
        return dt
        # return self.data.specificDate(self.userid)
    
    def getRiskProfile(self, name):
        self.risk_profile = self.data.getRiskProfile(name)

    def getPerformance(self, name):
        ret, vol = self.data.getPerformance(name)
        ret = ret if ret else 0
        vol = vol if vol else 0
        return ret, vol

    def page3Data(self, date):
        # latest가 False면 date에 해당하는 잔고 내역을 리턴한다.
        general, detail = self.data.returnPage3Data(self.name, date, latest=False)
        # print('---------------------general-----------------------')
        # print(general)
        # print('--------------------detail-----------------------------')
        # print(detail)
        return self.fullCond(general), detail

    def userList(self):
        users = self.data.uniqueUser()
        return [{'label': i, 'value': i} for i in users]

    def selections(self, name):
        # print('selection?? name is {}'.format(name))
        return self.data.getSelection(name)

    def closeData(self, point, date=None, name=None, choice=False):
        print(self.data.returnData(point, name, date, choice))
        result, user_id, name = self.data.returnData(point, name, date, choice)
        self.name = name
        self.userid = user_id
        # print('returnData() 에서 리턴한 userid: {}, name: {}'.format(self.userid, self.name))

        return result

        # risk_profile = self.data.getRiskProfile(name)
        # pf = self.data.advised_pf
        # max_dt = pf.loc[pf.risk_profile==2, ['date']].max().date

        # latest_advised_pf = pf.loc[(pf.risk_profile==2) & (pf.date==max_dt), :]
        # detail = self.data.getUserBalance(name)

        # if type(result) == str:
        #     return result

        # if choice:
        #     return result


        # before, after = result
        # before, after = self.fullCond(before), self.fullCond(after)

        # # if before.equals(after):
        # #     return before, after, False

        # return before, after

    def fullCond(self, data):
        condition = ['Cash', 'Equity', 'Fixed Income', 'Alternative']
        present = set(list(data['asset_class']))
        need = [col for col in condition if col not in present]
##
        if not need:
            return data

        date, user_id = data['date'].iloc[0], data['userid'].iloc[0]
        for col in need:
            data = data.append({'date': date, 'userid': user_id, 'asset_class': col,
                         'value': 0, 'wt': 0}, ignore_index=True)
        return data
