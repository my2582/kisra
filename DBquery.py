from pandas import DataFrame, Timestamp
from pandas.tseries.offsets import BDay
import numpy as np
import datetime

class query:
    def __init__(self, conn, con):
        self.conn = conn
        self.con = con

    def findDate(self, table, date, userid):
        # date 전날까지 데이터를 detail 테이블에서 조회해서 반환한다.
        query = "select distinct * from {0} where to_timestamp(%s,  'mm/dd/yyyy HH:M1:SS AM') > to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') and userid=%s"
        self.con.execute(query.format(table), [date, userid])
        self.conn.commit()
        return self.con.fetchall()


    def BetweenDate(self, table, dates, user):
        standard, start, end = dates
        standard = standard[:6]+'2021'+standard[8:]
        # print(standard)
        query = "select distinct * from {0} where to_timestamp(%s, 'mm/dd/yyyy HH:M1:SS AM') - interval %s <= to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') " \
                "and to_timestamp(%s, 'mm/dd/yyyy HH:M1:SS AM') - interval %s <= to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') and userid=%s"
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

    # def getUserRiskProfile(self, name):
    #     query = "select distinct profile_code from investors where name=%s"
    #     self.con.execute(query, [name])
    #     self.conn.commit()
    #     return self.con.fetchall()

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

        # 신규 가입자는 바로 영업일에 현금을 입금했다고 가정한다.
        # timestamp로 변환해서 직전 영업일을 얻고
        ts = pd.Timestamp(date)
        ts + BDay(-1)
        prev_date = ts + BDay(-1)
        date = prev_date.strftime('%Y-%m-%d') + ' 4:00:00 PM'

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

    def getUserBalance(self, userid, date=None, latest=True):
        # 마지막 날짜의 잔고를 detail 테이블에서 가져온다.
        # print('----in getUserBalance(), userid is {}'.format(userid))
        if latest:
            query = "select distinct * from detail A " \
                    "where to_timestamp(A.date, 'mm/dd/yyyy HH:M1:SS AM') = (select max(to_timestamp(B.date, 'mm/dd/yyyy HH:M1:SS AM')) from detail B group by B.userid " \
                    "having B.userid=%s) and A.userid=%s and A.wt > 0.0"
            self.con.execute(query, [userid, userid])
        else:
            query = "select distinct * from detail " \
                    "where to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') = to_timestamp(%s, 'mm/dd/yyyy HH:M1:SS AM') " \
                    "and userid=%s and wt > 0.0"
            self.con.execute(query, [date, userid])

        self.conn.commit()
        return self.con.fetchall()

    def getUserBalanceByName(self, name):
        query = "select distinct * from detail A " \
                "where to_timestamp(A.date, 'mm/dd/yyyy HH:M1:SS AM') = (select max(to_timestamp(B.date, 'mm/dd/yyyy HH:M1:SS AM')) from detail B group by B.name " \
                "having B.name=%s) and A.name=%s and A.wt > 0.0"

        self.con.execute(query, [name, name])
        self.conn.commit()
        return self.con.fetchall()

    def getUserGeneral(self, userid, date=None, latest=True):
        # 마지막 날짜의 요약잔고를 general 테이블에서 가져온다.
        if latest:
            query = "select distinct * from general A " \
                    "where to_timestamp(A.date, 'mm/dd/yyyy HH:M1:SS AM') = (select max(to_timestamp(B.date, 'mm/dd/yyyy HH:M1:SS AM')) from general B group by B.userid " \
                    "having B.userid=%s) and A.userid=%s and A.wt > 0.0"
            self.con.execute(query, [userid, userid])
        else:
            query = "select distinct * from general " \
                    "where to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') = to_timestamp(%s, 'mm/dd/yyyy HH:M1:SS AM') " \
                    "and userid=%s and wt > 0.0"
            self.con.execute(query, [date, userid])

        self.conn.commit()
        return self.con.fetchall()

    def getUserPerformance(self, userid):
        # 누적수익률과 연율화 변동성을 가져온다.
        query = "select exp(sum(R.ret))-1 as cum_ret, stddev(R.ret)*sqrt(250) as vol " \
                  "from (select A.ordered_date as date, ln(A.value/lag(A.value) OVER (ORDER BY A.ordered_date)) as ret " \
	                      "from (select B.ordered_date, sum(B.value) as value " \
			                      "from (select to_timestamp(date, 'mm/dd/yyyy HH:M1:SS AM') as ordered_date, value " \
				                          "from detail "\
				                 "where userid=%s order by ordered_date) B " \
                 "group by B.ordered_date) A) R"

        self.con.execute(query, [userid])
        self.conn.commit()
        return self.con.fetchall()