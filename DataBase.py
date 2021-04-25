import psycopg2
import os
from DBquery import query

class databaseDF:
    def __init__(self):
        try:
            self.dburl = os.environ['DATABASE_URL']
            self.conn = psycopg2.connect(self.dburl, sslmode='require')
        except:
            self.conn = psycopg2.connect(host='127.0.0.1', dbname='postgres', user='postgres', password='alstn121!', port='5432', sslmode='prefer')
            
        self.con = self.conn.cursor()
        self.query = query(self.conn, self.con)

    def createDefault(self, data):
        self.con.execute("CREATE TABLE IF NOT EXISTS general(date varchar(255), userid varchar(255), asset_class varchar(255), value float(24), wt float(24))")
        self.conn.commit()
        self.con.execute("CREATE TABLE IF NOT EXISTS detail(date varchar(255), userid varchar(255), name varchar(255), asset_class varchar(255), itemcode varchar(255), "
                                  "itemname varchar(255), quantity float(24), cost_price float(24), cost_value float(24), price float(24), value float(24), "
                                  "wt float(24), group_by varchar(255), original varchar(15))")
        self.conn.commit()
        self.con.execute("CREATE TABLE IF NOT EXISTS userselection(userid varchar(255), name varchar(255), set_no float(24), q_no float(24), answer float(24), risk_pref_value float(24))")        
        self.conn.commit()
        # self.con.execute("CREATE TABLE IF NOT EXISTS investors(userid varchar(255), name varchar(255), acc_no varchar(20), profile_code float(4))")
        ## self.conn.commit()

        self.con.execute("SELECT COUNT(*) FROM detail")
        self.conn.commit()

        x = self.con.fetchall()
        if not x[0][0]:
            self.insertDefault(data)
            self.conn.commit()

        self.con.execute("CREATE TABLE IF NOT EXISTS trade(date varchar(255), userid varchar(255), BS varchar(255), itemcode varchar(255), "
                                    "itemname varchar(255), quantity float(24), price float(24), value float(24))")
        self.conn.commit()


    def insertDefault(self, data):
        general, detail, user = data
        insert_query_gen = 'INSERT INTO {0} (date, userid, asset_class, value, wt) values (%s, %s, %s, %s, %s)'
        insert_query_dtl = 'INSERT INTO {0} (date, userid, name, asset_class, itemcode, itemname,' \
                           'quantity, cost_price, cost_value, price, value, wt, group_by, original) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

        insert_query_user = 'INSERT INTO {0} (userid, name, set_no, q_no, answer, risk_pref_value) values (%s, %s, %s, %s, %s, %s)'
        # insert_query_investors = 'INSERT INTO {0} (userid, name, acc_no, profile_code) values (%s, %s, %s, %s, %s)'

        general['value'] = general['value'].values.astype(float)
        general['wt'] = general['wt'].values.astype(float)

        detail['quantity'] = detail['quantity'].values.astype(float)
        detail['cost_price'] = detail['cost_price'].values.astype(float)
        detail['cost_value'] = detail['cost_value'].values.astype(float)

        user['set_no'] = user['set_no'].values.astype(float)
        user['q_no'] = user['q_no'].values.astype(float)
        user['answer'] = user['answer'].values.astype(float)
        user['risk_pref_value'] = user['risk_pref_value'].values.astype(float)

        # investors_m['profile_code'] = investors_m['profile_code'].values.astype(float)

        # print('----user is----')
        # print(user)

        # print('investors_m is -----')
        # print(investors_m)

        for i in range(len(general)):
            temp = general.iloc[i, :].values.tolist()
            self.con.execute(insert_query_gen.format('general'), temp)
            self.conn.commit()

        for i in range(len(detail)):
            temp = detail.iloc[i, :].values.tolist()
            self.con.execute(insert_query_dtl.format('detail'), temp)
            self.conn.commit()

        for i in range(len(user)):
            temp = user.iloc[i, :].values.tolist()
            self.con.execute(insert_query_user.format('userselection'), temp)
            self.conn.commit()

        return

    def getDate(self, user, date):
        value = self.query.findDate('detail', date, user)
        return value[-1][0]

    def getRecord(self, user, dates):
        # print('----in getRecord(), dates:{}, user:{}'.format(dates, user))
        record = self.query.BetweenDate('detail', dates, user)

        return record

    def getSelection(self, user):
        record = self.query.getUserSelection(user)
        return record

    def getUserList(self):
        record = self.query.getUserList()
        return record

    def newUser(self, answer, money, current_date=None, username=None):
        userid = self.query.newUser(answer, money, current_date, username)
        return userid

    # def getDetail(self, userid):
    #     record = self.query.getUserDetail(userid=userid)
    #     print('-------------detail------------------')
    #     print(userid)
    #     print(record)
    #     return record

    def getUserBalance(self, userid):
        record = self.query.getUserBalance(userid=userid)
        # print('-------------balance------------------')
        # print(userid)
        # print(record)
        return record

    def getUserGeneral(self, userid):
        record = self.query.getUserGeneral(userid=userid)
        # print('-------------general------------------')
        # print(userid)
        # print(record)
        return record

    def getUserRiskProfile(self, name):
        record = self.query.getUserRiskProfile(name)
        return record

    def insert_detail(self, new_detail):
        insert_query_dtl = 'INSERT INTO detail (itemcode, quantity, cost_price, price, cost_value, value, ' \
                           'itemname, asset_class, date, userid, name, group_by, original, wt) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

        new_detail['quantity'] = new_detail['quantity'].values.astype(float)
        new_detail['cost_price'] = new_detail['cost_price'].values.astype(float)
        new_detail['cost_value'] = new_detail['cost_value'].values.astype(float)
        new_detail['price'] = new_detail['price'].values.astype(float)
        new_detail['value'] = new_detail['value'].values.astype(float)
        new_detail['wt'] = new_detail['wt'].values.astype(float)

        # 날짜형식 변환
        new_detail.date = new_detail.date.map(lambda x:str(x.month)+'/'+str(x.day)+'/'+str(x.year)+ ' 4:00:00 PM')

        col_order = ['itemcode', 'quantity', 'cost_price', 'price', 'cost_value', 'value', 'itemname', 'asset_class', 'date', 'userid', 'username', 'group_by', 'original', 'wt']
        # print(new_detail.loc[:, col_order])

        for idx, row in new_detail.iterrows():
            temp = row[col_order].values.tolist()
            self.con.execute(insert_query_dtl, temp)
            self.conn.commit()
    
    def insert_general(self, new_general):
        insert_query_gen = 'INSERT INTO general (date, userid, asset_class, value, wt) values (%s, %s, %s, %s, %s)'

        # 날짜형식 변환
        new_general.date = new_general.date.map(lambda x:str(x.month)+'/'+str(x.day)+'/'+str(x.year)+ ' 4:00:00 PM')

        for idx, row in new_general.iterrows():
            temp = row[['date', 'userid', 'asset_class', 'value', 'wt']].values.tolist()
            self.con.execute(insert_query_gen, temp)
            self.conn.commit()

    def getMaxDate(self, name):
        # 최근 잔고를 이름으로 불러와서 최근 날짜를 이용할 수 있게 한다.
        return self.query.getUserBalanceByName(name)

    # def insert_investor(self, userid, name, profile_code):
    #     insert_query_inv = 'INSERT INTO investors (userid, name, acc_no, profile_code) values (%s, %s, %s, %s)'

    #     self.con.execute(insert_query_inv, [userid, name, '', profile_code])
    #     self.conn.commit()
