import numpy as np
import pandas as pd

old_port = pd.read_csv('./docs/old_port.dat', header=0)
new_port = pd.read_csv('./docs/new_port.dat', header=0)


def reduce_obvious_costs(old_port, new_port):
    r"""
    현재 포트폴리오 구성(old_port) 추천 포트폴리오 구성(new_port)를 입력받아
    불필요한 매매비용을 줄이도록 종목코드를 변경한다.

    예를 들어 KINDEX 200 10% -> KODEX 200 15%로 바꾸는 것은 매도 10%, 매수 15%를 해야 된다.
    이 둘은 사실상 같은 투자효과를 내므로 EM_M_KR_LARGE라는 exposure로 분류되어 있으므로,
    KINDEX 10% -> KINDEX 15%로 바꿔 생각하면 매수 5%만 해도 된다.
    따라서 20%에 대한 매매비용이 절약된다. 이는 최적화라기보다는 명백한 잘못을 하지 말아야 되는
    기본 기능으로 분류된다.

    Parameters
    ----------
    old_port : pd.DataFrame
        현재 포트폴리오. 컬럼으로 ['exposure', 'itemcode', 'wt']가 필요함.
    new_port : pd.DataFrame
        추천(미래) 포트폴리오. 컬럼으로 ['exposure', 'itemcode', 'wt']가 필요함.

    Return
    ------
    pd.DataFrame
    불필요한 매매비용이 줄도록 new_port의 itemcode를 적절히 변경하고,
    old_port와 new_port를 병합하여 1개의 DataFrame 인스턴스를 반환.
    """

    # 두 포트폴리오 병합하고 & nan 처리
    old_new = pd.merge(old_port.loc[:, ['exposure', 'itemcode', 'wt']], new_port.loc[:, ['exposure', 'itemcode', 'wt']],
                       left_on=['exposure'], right_on=['exposure'], how='outer', suffixes=['_old', '_new'])

    old_new = old_new.fillna(value={'wt_old': 0, 'wt_new': 0})
    old_new['wt_diff'] = np.abs(old_new['wt_new'] - old_new['wt_old'])

    exposures = set(old_new.exposure)

    for exp in exposures:
        exp_grp = old_new[old_new.exposure == exp].reset_index(drop=True)

        print('exp_grp: {}'.format(exp_grp))
        used_itemcode_old = []

        for itemcode_new in set(exp_grp.itemcode_new):
            # if exp_grp.loc[~exp_grp.itemcode_old.isin(used_itemcode_old)].empty:
            #     break

            # wt_diff 값이 가장 작은 레코드 선정
            # "매칭됐다"고 표현하겠음. 가장 작은 wt_diff를 갖는 old_port와 new_port가 매칭됐다.
            sorted_idx = exp_grp.loc[exp_grp.itemcode_new==itemcode_new].wt_diff.argsort().tolist()[0]
            smallest_diff = exp_grp.loc[sorted_idx]

            # search_over = exp_grp.loc[exp_grp.itemcode_new==itemcode_new]
            # if search_over.loc[~search_over.itemcode_old.isin(used_itemcode_old)].shape[0] > 0:
            #     break
            # else:
            #     sorted_idx = search_over.loc[~exp_grp.itemcode_old.isin(used_itemcode_old)].wt_diff.argsort().tolist()[0]
            #     smallest_diff = search_over.loc[sorted_idx]


            # wt_diff가 가장 작은 종목코드를 old_port에서 찾아서
            # 매칭된 wt_diff 레코드의 itemcode_new값을 덮어쓴다.
            # temp = new_port.loc[(new_port.exposure == smallest_diff.exposure) & (
            #     new_port.itemcode == smallest_diff.itemcode_new), 'itemcode'].values[0]
            # temp_idx = new_port.loc[(new_port.exposure == smallest_diff.exposure) & (
            #     new_port.itemcode == smallest_diff.itemcode_new), 'itemcode'].index

            new_port.loc[(new_port.exposure == smallest_diff.exposure) & (
                new_port.itemcode == smallest_diff.itemcode_new), 'itemcode'] = smallest_diff.itemcode_old
            
            used_itemcode_old.append(smallest_diff.itemcode_old)

            # exp_grp = exp_grp.loc[exp_grp.index.drop(exp_grp.index[exp_grp.itemcode_new==temp])]
            # if not exp_grp.empty:
            #     exp_grp.loc[temp_idx, 'itemcode_new'] = temp 
            # old_new = old_new.loc[old_new.index.drop(old_new.index[(old_new.exposure == smallest_diff.exposure) & (
            #     old_new.itemcode_new == smallest_diff.itemcode_new)]), :]

    return old_port, new_port


old_p, new_p = reduce_obvious_costs(old_port, new_port)

print('old_port: {}'.format(old_p))
print('new_port: {}'.format(new_p))
