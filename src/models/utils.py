import pandas as pd
from load_data import Singleton, Balance, Instruments, PriceDB, AdvisedPortfolios
from client import Client


def get_asset_classes(instruments):
    r"""
    Riskfolio 패키지에서 제약조건을 걸 때 필요한 
    데이터 프레임 인스턴스 asset_classes를
    instruments를 이용해 만들어 반환한다.

    참조: https://riskfolio-lib.readthedocs.io/en/latest/constraints.html

    Parameters:
    instruments: pd.DataFrame
        - 투자 유니버스 중 거래가능한 종목들의 집합

    Returns:
    asset_classes: pd.DataFrame
        - ConstraintsFunctions.assets_constraints의 두 번째 파라미터 값
    """
    asset_classes = instruments[[
        'itemcode', 'asset_class', 'dc_risky_asset', 'issuer', 'strategy']]
    asset_classes = asset_classes.rename(
        columns={
            'itemcode': 'Assets',
            'asset_class': 'Asset class',
            'dc_risky_asset': 'DC risky asset',
            'issuer': 'Issuer',
            'strategy': 'Strategy'
        })

    return asset_classes


def get_current_pos(userid, latest_balance=None):
    r"""
    이용자의 포트폴리오 포지션 정보를 최근 잔고를 기준으로 추출하여 반환한다.
    포트폴리오 포지션 구성:
      - 종목코드(itemcode)
      - 종목명(itemname)
      - 비중(wt)
      - 평가액(value)
      - 수량(quantity)
      - 가격(price)

    Parameters:
    userid : str
        이용자 아이디
    balance_s : pd.DataFrame
        상세잔고 테이블
    """

    if latest_balance is not None:  # 이 이용자의 최근 잔고내역을 정확하게 주면
        balance = latest_balance
    else:
        # Balance.instance()는 전 사용자의 잔고 상세내역 테이블의 인스턴스 반환.
        balance_s = Balance.instance().data

        # balance에 사용자(userid)의 최근 잔고 내역 저장
        balance = balance_s.loc[(balance_s.userid == userid) & (
            balance_s.date == balance_s.groupby(by='userid')['date'].max()[userid])]

    balance = balance.drop(['userid', 'name', 'asset_class',
                            'group_by', 'principal', 'cost_price', 'cost_value'], axis=1)

    # 추가할 컬럼 추가
    col_to_add = ['tracking_code', 'exposure']
    instruments_m = Instruments.instance().data
    balance = balance.merge(instruments_m.loc[:, ['itemcode']+col_to_add], left_on='itemcode', right_on='itemcode', how='left')

    return balance


def get_advised_port(risk_profile, df_advised_ports=None):
    r"""
    로보 포트폴리오 데이터(data)에서 risk_profile에 맞는 포트폴리오를
    추천 가능한 가장 최근일 기준으로 반환한다.

    Parameters:
    -----------
    risk_profile : int
        투자자성향 분류번호
    advised_portfolios : pd.DataFrame
        로보 포트폴리오 데이터. 투자자성향(risk_profile)별로 매일 추천 포트폴리오
        데이터가 존재한다.

    Returns:
    -------
    pd.DataFrame : risk_profile에 맞는 최근일자 추천 포트폴리오를 반환한다.
    """

    if df_advised_ports is not None:
        df = df_advised_ports
    else:
        df = AdvisedPortfolios.instance().data

    advised_pf = df.loc[(df.risk_profile == risk_profile) & (
        df.date == df.groupby(by='risk_profile')['date'].max()[risk_profile])]
    advised_pf = advised_pf.rename(columns={'weights': 'wt'})

    advised_pf = advised_pf.drop(['risk_profile'], axis=1)

    # 추가할 컬럼
    col_to_add = ['exposure']
    instruments_m = Instruments.instance().data
    advised_pf = advised_pf.merge(instruments_m.loc[:, ['itemcode']+col_to_add], left_on='itemcode', right_on='itemcode', how='left')

    # Price DB와 병합하기 위해서 컬럼 타입을 맞추기 위해 advised_pf 테이블의 date 컬럼 타입을 datetime으로 바꾼다.
    advised_pf.loc[:, 'date'] = pd.to_datetime(advised_pf.date)

    # 가격/거래량/거래대금 정보 추가
    price_db = PriceDB.instance().data
    advised_pf = advised_pf.merge(price_db, left_on=['date', 'itemcode'], right_on=['date', 'itemcode'], how='left')

    return advised_pf.drop(['ret'], axis=1)


def get_recommendation(client):

    pass
