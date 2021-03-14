import numpy as np
import pandas as pd

class User:
    r"""
    투자자 클래스이다. 투자자 1명이 1개의 투자성향값을 갖고, 이에 따라 RA에 포트폴리오를 추천받는다.
    투자성향값이 같으면 추천받는 포트폴리오가 같다.

    Parameters
    ----------
    accounts : list
        계좌번호를 원소로하는 리스트임. 계좌번호는 str이다.
        예) ['800-01', '810-01']
    
    book_s : dict
        계좌번호를 key로 하고, 원장 상세 테이블(DataFrame)을 value로 하는 딕셔너리이다.
        원장 상세 테이블은 book_s
    """

    def __init__(self,
        userid=None,
        username=None,
        accounts=None
    ):
        self.userid = userid
        self.username = username
        self.accounts = accounts
    
    def add_acc_no(self, acc_no):
        self.accounts[acc_no]


    @property
    def userid(self):
        if self.userid is not None and isinstance(self.userid, str):
            return self.userid
        else:
            raise NameError('userid must be a str.')
    
    @userid.setter
    def userid(self, value):
        if value is not None and isinstance(value, str):
            self.userid = value
        else:
            raise NameError('userid must be a str.')

    @property
    def username(self):
        if self.username is not None and isinstance(self.username, str):
            return self.username
        else:
            raise NameError('username must be a str.')
    
    @username.setter
    def username(self, value):
        if value is not None and isinstance(value, str):
            self.username = value
        else:
            raise NameError('username must be a str.')
