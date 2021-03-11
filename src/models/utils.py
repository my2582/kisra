import pandas as pd

def get_asset_classes(instruments):
    '''
    Riskfolio 패키지에서 제약조건을 걸 때 필요한 
    데이터 프레임 인스턴스 asset_classes를 instruments로부터 만들어
    반환한다.

    참조: https://riskfolio-lib.readthedocs.io/en/latest/constraints.html

    Parameters:
    instruments: pd.DataFrame
        - 투자 유니버스 중 거래가능한 종목들의 집합


    Returns:
    asset_classes: pd.DataFrame
        - ConstraintsFunctions.assets_constraints의 두 번째 파라미터 값
    '''
    asset_classes = instruments[['itemcode', 'asset_class', 'dc_risky_asset', 'issuer', 'strategy']]
    asset_classes = asset_classes.rename(
        columns={
            'itemcode': 'Assets',
            'asset_class': 'Asset class',
            'dc_risky_asset': 'DC risky asset',
            'issuer': 'Issuer',
            'strategy': 'Strategy'
        })
    
    return asset_classes