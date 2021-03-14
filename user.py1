from data import Data


class User:
    def __init__(self):
        self.data = Data.Data()
        self.name, self.date = self.data.defaults()

    def getStartDate(self):
        return self.data.specificDate(self.name)

    def changedUserData(self, data):
        return self.data.changeSingleData(data)

    def page3Data(self, date):
        general, detail = self.data.returnPage3Data(self.name, date)
        return self.fullCond(general), detail

    def userList(self):
        users = self.data.uniqueUser()
        return [{'label': i, 'value': i} for i in users]

    def closeData(self, point, choice=False):
        result = self.data.returnData(point, self.name, self.date, choice)

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

        if not need:
            return data

        date, user_id = data['date'].iloc[0], data['userid'].iloc[0]
        for col in need:
            data = data.append({'date' : date, 'userid' : user_id, 'asset_class' : col,
                         'value' : 0, 'wt' : 0}, ignore_index=True)
        return data
