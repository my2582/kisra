from pandas import DataFrame
import numpy as np

class query:
    def __init__(self, conn, con):
        self.conn = conn
        self.con = con

    def findDate(self, table, date, userid):
        query = "select * from {0} where to_timestamp(%s,  'mm/dd/yyyy HH:M1:SS AM') > to_timestamp(date,  'mm/dd/yyyy HH:M1:SS AM')" \
                "inner join on {1}.userid = %s"
        self.con.execute(query.format(table, table), [date, userid])
        self.conn.commit()
        return self.con.fetchall()


    def BetweenDate(self, table, dates, user):
        standard, start, end = dates
        query = "select * from {0} where to_timestamp(%s,  'mm/dd/yyyy HH:M1:SS AM') BETWEEN to_timestamp(%s,  'mm/dd/yyyy HH:M1:SS AM') - interval %s+' day'" \
                "and to_timestamp(%s,  'mm/dd/yyyy HH:M1:SS AM') - interval %s +' day'" \
                " join on {1}.userid = %s"
        self.con.execute(query.format(table, table), [standard, start, end, user])
        self.conn.commit()
        return DataFrame(np.array(self.con.fetchall()))

    def newUser(self):
        pass
