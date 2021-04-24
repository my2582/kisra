from pandas import DataFrame
import numpy as np
import datetime

class query:
    def __init__(self, conn, con):
        self.conn = conn
        self.con = con

    def findDate(self, table, date, userid):
        query = "select distinct * from {0} where to_timestamp(%s,  'mm/dd/yyyy HH:M1:SS AM') > to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') and userid=%s"
        self.con.execute(query.format(table), [date, userid])
        self.conn.commit()
        return self.con.fetchall()


    def BetweenDate(self, table, dates, user):
        standard, start, end = dates
        standard = standard[:6]+'2021'+standard[8:]
        print(standard)
        query = "select distinct * from {0} where to_timestamp(%s, 'mm/dd/yyyy HH:M1:SS AM') - interval %s <= to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') " \
                "and to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') <= to_timestamp(%s, 'mm/dd/yyyy HH:M1:SS AM') - interval %s and userid=%s"
        self.con.execute(query.format(table),  [standard, str(start)+' days', standard, str(end) +' days', user])
        self.conn.commit()
        return DataFrame(np.array(self.con.fetchall()))

    def getUserSelection(self, user):
        query = "select distinct answer from userselection where userid=%s"
        self.con.execute(query, [user])
        self.conn.commit()
        return self.con.fetchall()

    def getUserList(self):
        query = "select distinct userid, name from userselection"
        self.con.execute(query)
        self.conn.commit()
        return self.con.fetchall()

    def getUserRiskProfile(self, name):
        query = "select distinct profile_code from investors where name=%s"
        self.con.execute(query, [name])
        self.conn.commit()
        return self.con.fetchall()

    def newUser(self, answers, money, current_date=None, username=None):
        query = "select distinct userid from userselection"
        self.con.execute(query)
        self.conn.commit()
        id = 0
        for i in self.con.fetchall():
            temp = i[0][-2:]
            if id<int(temp):
                id = int(temp)
        id += 1
        now = datetime.datetime.now()
        hour, timezone, type_hour = now.hour, 'AM', ''
        if 12<now.hour:
            hour -= 12
            timezone = 'PM'
        if now.hour<10:
            type_hour = '0'+str(now.hour)

        if current_date is None:
            date = str(now.month)+'/'+str(now.day)+'/'+str(now.year)+' '+str(hour)+':'+str(now.minute)+':'+str(now.second)+' '+timezone 
        else:
            dt = datetime.datetime.strptime(current_date, '%Y-%m-%d')
            date = str(dt.month)+'/'+str(dt.day)+'/'+str(dt.year)+' 4:00:00 PM'

        userid='A' + ('00' + str(id))[-3:]
        query = "INSERT INTO userselection(userid, name, set_no, q_no, answer, risk_pref_value) values (%s, %s, %s, %s, %s, %s)"
        for i in range(8):
            self.con.execute(query, [userid, username, float(1), float(i+1), float(answers[i][0]), float(answers[i][1])])
            self.conn.commit()

        query = "INSERT INTO detail (date, userid, name, asset_class, itemcode, itemname, quantity, cost_price, cost_value, price, value, wt, group_by, original) " \
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        self.con.execute(query, [date, userid, username, 'Cash', 'C000001', '현금', float(money), float(1), float(money),
                                 float(1), float(money), float(1),
                                 str(now.year)+str(now.month)+str(now.day)+type_hour+':'+str(now.minute)+'Cash', 'Y'])
        self.conn.commit()

        query = "INSERT INTO general(date, userid, asset_class, value, wt) values (%s, %s, %s, %s, %s)"
        self.con.execute(query, [date, userid, 'Cash', float(money), float(1)])
        self.conn.commit()

        return userid

    def getUserDetail(self, userid):
        query = "select distinct * from detail A where A.userid=%s and A.date=(select max(date) from detail where userid=%s)"
        self.con.execute(query, [userid, userid])
        self.conn.commit()
        return self.con.fetchall()

    def getUserBalance(self, userid):
        print('----in getUserBalance(), userid is {}'.format(userid))
        query = "select distinct * from detail A " \
                "where to_timestamp(A.date, 'mm/dd/yyyy HH:M1:SS AM') = (select max(to_timestamp(B.date, 'mm/dd/yyyy HH:M1:SS AM')) from detail B group by B.userid " \
                "having B.userid=%s) and A.userid=%s and A.wt > 0.0"

        self.con.execute(query, [userid, userid])
        self.conn.commit()
        return self.con.fetchall()

    def getUserBalanceByName(self, name):
        print('----in getUserBalance(), name is {}'.format(name))
        query = "select distinct * from detail A " \
                "where to_timestamp(A.date, 'mm/dd/yyyy HH:M1:SS AM') = (select max(to_timestamp(B.date, 'mm/dd/yyyy HH:M1:SS AM')) from detail B group by B.name " \
                "having B.name=%s) and A.name=%s and A.wt > 0.0"

        self.con.execute(query, [name, name])
        self.conn.commit()
        return self.con.fetchall()
