from datetime import date, timedelta
import ReadWrite
import pandas as pd

class User:
    def __init__(self):
        self.file = ReadWrite.ReadWrite()
        self.name = '투자자1'
        self.start_time = '1/10/2020 1:00:00'
        self.file_name = 'balance_s.pkl'

    def select(self):
        data = pd.read_pickle(self.file.returnData(self.file_name))

        return