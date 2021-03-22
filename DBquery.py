from pandas import DataFrame
import numpy as np
import datetime

class query:
    def __init__(self, conn, con):
        self.conn = conn
        self.con = con

    def findDate(self, table, date, userid):
        query = "select * from {0} where to_timestamp(%s,  'mm/dd/yyyy HH:M1:SS AM') > to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') and userid=%s"
        self.con.execute(query.format(table), [date, userid])
        self.conn.commit()
        return self.con.fetchall()


    def BetweenDate(self, table, dates, user):
        standard, start, end = dates
        standard = standard[:6]+'2021'+standard[8:]
        print(standard)
        query = "select * from {0} where to_timestamp(%s, 'mm/dd/yyyy HH:M1:SS AM') - interval %s <= to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') " \
                "and to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') <= to_timestamp(%s, 'mm/dd/yyyy HH:M1:SS AM') - interval %s and userid=%s"
        self.con.execute(query.format(table),  [standard, str(start)+' days', standard, str(end) +' days', user])
        self.conn.commit()
        return DataFrame(np.array(self.con.fetchall()))

    def getUserSelection(self, user):
        query = "select answer from userselection where userid=%s"
        self.con.execute(query, [user])
        self.conn.commit()
        return self.con.fetchall()

    def newUser(self, answers, money):
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

        date = str(now.month)+'/'+str(now.day)+'/'+str(now.year)+' '+str(hour)+':'+str(now.minute)+':'+str(now.second)+' '+timezone

        query = "INSERT INTO userselection(userid, set_no, q_no, answer, risk_pref_value) values (%s, %s, %s, %s, %s)"
        for i in range(8):
            self.con.execute(query, ['A'+str(id), float(1), float(i+1), float(answers[i][0]), float(answers[i][1])])
            self.conn.commit()

        query = "INSERT INTO detail (date, userid, name, asset_class, itemcode, itemname, quantity, cost_price, cost_value, price, value, wt, group_by, original) " \
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        self.con.execute(query, [date, 'A'+str(id), '투자자'+str(id), '현금성', 'C000001', '현금', float(money), float(1), float(money),
                                 float(1), float(money), float(1),
                                 str(now.year)+str(now.month)+str(now.day)+type_hour+':'+str(now.minute)+'현금성', 'Y'])
        self.conn.commit()

        query = "INSERT INTO general(date, userid, asset_class, value, wt) values (%s, %s, %s, %s, %s)"
        self.con.execute(query, [date, 'A'+str(id), '현금성', float(money), float(1)])
        self.conn.commit()

        return

    def insert_advised_pf(self, pf):
        query = "INSERT INTO advised_pf(date, risk_profile, itemcode, weights, tracking_code, itemname, price, volume, trading_amt_mln, asset_class varchar) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        for row in pf:
            self.con.execute(query, [row.date, row.risk_profile, row.itemcode, row.weights, row.tracking_code, row.itemname, row.price, row.volume, row.trading_amt_mln, row.asset_class])
            self.conn.commit()

        return