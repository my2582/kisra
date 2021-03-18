import psycopg2
import os
from DBquery import query

class databaseDF:
    def __init__(self):
        self.dburl = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(self.dburl, sslmode='require')
        # self.conn = psycopg2.connect(host='127.0.0.1', dbname='postgres', user='postgres', password='kus410028@', port='5432', sslmode='prefer')
        self.con = self.conn.cursor()
        self.query = query(self.conn, self.con)

    def createDefault(self, data):
        print(data)
        self.con.execute("CREATE TABLE IF NOT EXISTS general(date varchar(255), userid varchar(255), asset_class varchar(255), value float(24), wt float(24))")
        self.con.execute("CREATE TABLE IF NOT EXISTS detail(date varchar(255), userid varchar(255), name varchar(255), asset_class varchar(255), "
                                  "itemname varchar(255), quantity float(24), cost_price float(24), cost_value float(24), price float(24), value float(24), "
                                  "wt float(24), group_by varchar(255), original varchar(5))")
        self.con.execute("CREATE TABLE IF NOT EXISTS USER(userid varchar(255), set_no float(24), q_no float(24), answer float(24), risk_pref_value float(24))")

        self.insertDefault(data)
        self.conn.commit()

    def insertDefault(self, data):
        general, detail, user = data
        insert_query_gen = 'INSERT INTO {0} (date, userid, asset_class, value, wt) values (%s, %s, %s, %s, %s)'
        insert_query_dtl = 'INSERT INTO {0} (date, userid, name, asset_class, itemcode, itemname,' \
                           'quantity, cost_price, cost_value, price, value, wt, group_by, original) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

        insert_query_user = 'INSERT INTO {0} (userid, set_no, q_no, answer, risk_pref_value) values (%s, %s, %s, %s, %s)'

        detail['quantity'] = detail['quantity'].values.astype(float)
        detail['cost_price'] = detail['cost_price'].values.astype(float)
        detail['cost_value'] = detail['cost_value'].values.astype(float)

        user['set_no'] = user['set_no'].values.astype(float)
        user['q_no'] = user['q_no'].values.astype(float)
        user['answer'] = user['answer'].values.astype(float)
        user['risk_pref_value'] = user['risk_pref_value'].values.astype(float)

        for i in range(len(general)):
            temp = general.iloc[i, :].values.tolist()
            self.cur.execute(insert_query_gen.format('general'), temp)

        for i in range(len(detail)):
            temp = general.iloc[i, :].values.tolist()
            self.cur.execute(insert_query_dtl.format('detail'), temp)

        for i in range(len(user)):
            temp = user.iloc[i, :].values.tolist()
            self.cur.execute(insert_query_user.format('user'), temp)
        return

    def getDate(self, user, date):
        value = self.query.findDate('detail', date, user)
        return value[-1][0]

    def getRecord(self, user, dates):
        record = self.query.BetweenDate('detail', dates, user)
        return record
