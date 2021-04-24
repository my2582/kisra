from data import Data


class User:
    def __init__(self):
        self.data = Data()
        self.name, self.date, self.userid = self.data.defaults()

    def getStartDate(self, name):
        dt = self.data.specificDate(name)
        print('---in getStartDate(), last record for {} is {}'.format(name, dt))
        return dt
        # return self.data.specificDate(self.userid)
    
    def getRiskProfile(self, name):
        self.risk_profile = self.data.getRiskProfile(name)

    def page3Data(self, date):
        general, detail = self.data.returnPage3Data(self.name, date)
        print('---------------------general-----------------------')
        print(general)
        print('--------------------detail-----------------------------')
        print(detail)
        return self.fullCond(general), detail

    def userList(self):
        users = self.data.uniqueUser()
        return [{'label': i, 'value': i} for i in users]

    def selections(self, name):
        return self.data.getSelection(name)

    def closeData(self, point, date=None, name=None, choice=False):
        result = self.data.returnData(point, name, date, choice)

        # risk_profile = self.data.getRiskProfile(name)
        # pf = self.data.advised_pf
        # max_dt = pf.loc[pf.risk_profile==2, ['date']].max().date

        # latest_advised_pf = pf.loc[(pf.risk_profile==2) & (pf.date==max_dt), :]
        # detail = self.data.getUserBalance(name)

        if type(result) == str:
            return result

        if choice:
            return result

        before, after = result
        before, after = self.fullCond(before), self.fullCond(after)

        # if before.equals(after):
        #     return before, after, False

        return before, after

    def fullCond(self, data):
        condition = ['현금성', '주식', '채권', '대체']
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
