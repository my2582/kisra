import dash
import dash_html_components as html
from character import Character
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import layout
from user import User
import numpy as np
from datetime import timedelta, datetime
import plotly.graph_objects as go
from DataBase import databaseDF
from src.models.load_data import AdvisedPortfolios, Singleton, PriceDB
from skimage import io
from pandas import to_numeric, to_datetime

sheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=sheet,
                suppress_callback_exceptions=True)
server = app.server
user = User()


def show_content(users):
    # app = self.app
    style = layout.style
    tab = layout.tab
    origin = tab
    user = users
    app.layout = origin

    # db = databaseDF()
    # advised_pf = AdvisedPortfolios.instance().data
    # print('type(advised_pf)'.format(type(advised_pf)))
    # print('Here is your advised_pf:')
    # print(advised_pf.tail(3))
    # db.insert_advised_pf(advised_pf)

    @app.callback(
        Output(layout.output_id, 'children'),
        Input(layout.input_id, "value"),
    )
    def show_page(tab_input):
        if tab_input == 'signup':
            app.layout.children[-1] = html.Div(layout.signup)
            userList = user.userList()
            layout.signup[1].children[1].options = userList + ['x']

            return html.Div(layout.signup)

        if tab_input == 'analysis':
            app.layout.children[-1] = html.Div(layout.analysis)
            userList = user.userList()
            layout.analysis[0].children[1].options = userList
            layout.analysis[0].children[3].value = user.date
            return html.Div(layout.analysis)

        if tab_input == 'info':
            app.layout.children[-1] = html.Div(layout.info)
            userList = user.userList()
            layout.info[0].children[1].options = userList
            layout.info[0].children[1].value = user.name
            return html.Div(layout.info)

    @app.callback(
        Output('output-div', 'children'),
        Input('submit-val', 'n_clicks'),
        State('self-understand-degree', 'value'),
        State('age-check', 'value'),
        State('invest-terms', 'value'),
        State('finance-ratio', 'value'),
        State('annual-income', 'value'),
        State('character-risk', 'value'),
        State('invest-purpose', 'value'),
        State('invest-experience', 'value'),
        State('invest-scale', 'value'),
        State('datetime', 'value'),
        State('name', 'value')
    )
    def page1_result(n_clicks, input_1, input_2, input_3, input_4,
                     input_5, input_6, input_7, input_8, input_9, input_10,
                     input_11):

        def get_fig(source, width, height):
            # Create figure
            fig = go.Figure()

            # Constants
            img_width = width
            img_height = height
            scale_factor = 0.5

            # Add invisible scatter trace.
            # This trace is added to help the autoresize logic work.
            fig.add_trace(
                go.Scatter(
                    x=[0, img_width * scale_factor],
                    y=[0, img_height * scale_factor],
                    mode="markers",
                    marker_opacity=0
                )
            )

            # Configure axes
            fig.update_xaxes(
                visible=False,
                range=[0, img_width * scale_factor]
            )

            fig.update_yaxes(
                visible=False,
                range=[0, img_height * scale_factor],
                # the scaleanchor attribute ensures that the aspect ratio stays constant
                scaleanchor="x"
            )

            # Add image
            fig.add_layout_image(
                dict(
                    x=0,
                    sizex=img_width * scale_factor,
                    y=img_height * scale_factor,
                    sizey=img_height * scale_factor,
                    xref="x",
                    yref="y",
                    opacity=1.0,
                    layer="below",
                    sizing="stretch",
                    source=source)
            )

            # Configure other layout
            fig.update_layout(
                width=img_width * scale_factor,
                height=img_height * scale_factor,
                margin={"l": 0, "r": 0, "t": 0, "b": 0},
            )

            return fig

        if 0 < n_clicks:
            tags_id = [input_1, input_2, input_3, input_4, input_5, input_6, input_7, input_8, input_9,
                       input_10, input_11]
            character = Character(tags_id)
            # print('tags_id: {}'.format(tags_id))
            assert app.layout.children[-1] is not None, "app.layout is none."
            output = html.Div([
                html.Div(id='character-result')
            ], id='output-div')
            if character.empty_check():
                # fig_rpt = go.Figure(go.Image(dx=1008, dy=2592, z=io.imread('./reports/figures/report-4_2021-02-26.png')))
                # fig_rpt2 = go.Figure(go.Image(dx=1000, dy=600, z=io.imread('./reports/figures/ef_area-4_2021-02-26.png')))
                # fig_rpt3 = go.Figure(go.Image(dx=640, dy=480, z=io.imread('./reports/figures/ef-4_2021-02-26.png')))
                # fig_rpt = go.Figure().add_layout_image(source='./reports/figures/report-4_2021-02-26.png')
                # fig_rpt2 = go.Figure().add_layout_image(source='./reports/figures/ef_area-4_2021-02-26.png')
                # fig_rpt3 = go.Figure().add_layout_image(source='./reports/figures/ef-4_2021-02-26.png')

                answer = []
                for_selected = layout.signup[3]
                for id in tags_id:
                    check = False
                    for i in range(1, len(for_selected.children), 3):
                        for j in range(len(for_selected.children[i].options)):
                            if for_selected.children[i].options[j]['value'] == id:
                                answer.append(j+1)
                                check = True
                                break
                        if check:
                            break

                risk_avg, df, by_assetclass, score, current_date, risk_profile = character.predict(
                    answer, first_trade=True)
                rpt_url = 'https://raw.githubusercontent.com/my2582/kisra_storage/main/report-{}_{}.png'.format(risk_profile, current_date)
                rpt2_url = 'https://raw.githubusercontent.com/my2582/kisra_storage/main/ef_area-{}_{}.png'.format(risk_profile, current_date)
                rpt3_url = 'https://raw.githubusercontent.com/my2582/kisra_storage/main/ef-{}_{}.png'.format(risk_profile, current_date)
                # print('URLs:', rpt_url, rpt2_url, rpt3_url)
                fig_rpt = get_fig(source=rpt_url, width=1008, height=2592)
                fig_rpt2 = get_fig(source=rpt2_url, width=1000, height=600)
                fig_rpt3 = get_fig(source=rpt3_url, width=640, height=480)
                
                result = '당신의 점수는 {0}이며 {1}형 투자자입니다. 당신에게 맞는 포트폴리오를 확인해 보세요'.format(
                    score, risk_avg)
                # 파이차트 (종목별)
                pie = px.pie(df, names=df.loc[:, 'itemname'], values=df.loc[:, 'weights'],
                             title="추천 포트폴리오", color_discrete_sequence=px.colors.qualitative.Set3)

                # print('-=-=-=-df.columns-=-=-=-=-')
                # print(df.columns)

                # 바 차트(자산군별)
                bar_chart = px.bar(by_assetclass, y='weights', x='asset_class', title='자산군별 비중',
                                   labels={'asset_class': '자산군', 'weights': '비중'},
                                   orientation='v', color="asset_class", color_continuous_scale='darkmint',
                                   template='plotly_dark')
                output.children[0].children = result



                if len(output.children) < 3:
                    fig = dcc.Graph(id='pie-chart')
                    fig.figure = pie
                    fig.figure.layout.paper_bgcolor = style['pie_chart_style']['backgroundColor']

                    fig_bar = dcc.Graph(id='bar-chart')
                    fig_bar.figure=bar_chart
                    fig_bar.figure.layout.paper_bgcolor = style['pie_chart_style']['backgroundColor']
                    output.children.append(fig)
                    output.children.append(fig_bar)

                # print('------------fig---------------')
                # fig_show = html.Img(class_='picture-show', src="./reports/figures/report-4_2021-02-26.png")
                # href = html.A('Download readMe.pdf', download='./reports/figures/report-4_2021-02-26.png', href='/readMe.pdf')
                # output.children.append(href)
                output.style = style['pie_chart_style']
                # fig_rpt['layout'].update(width=1008, height=2592, autosize=False)
                # fig_rpt2['layout'].update(width=1000, height=600, autosize=False)
                # fig_rpt3['layout'].update(width=640, height=480, autosize=False)
                output.children.append(dcc.Graph(id="fig-image", figure=fig_rpt, config={'doubleClick': 'reset'}))
                output.children.append(dcc.Graph(id="fig2-image", figure=fig_rpt2, config={'doubleClick': 'reset'}))
                output.children.append(dcc.Graph(id="fig3-image", figure=fig_rpt3, config={'doubleClick': 'reset'}))
                return output

            warning = '비어있는 항목이 있습니다! 전부 체크해 주세요'
            if 2 < len(output.children):
                output.children = output.children[:-1]
            output.children[0].children = warning
            output.style = style['pie_chart_style']
            return output

    @app.callback(
        [
            Output('invest-experience', 'value'),
            Output('invest-purpose', 'value'),
            Output('character-risk', 'value'),
            Output('annual-income', 'value'),
            Output('finance-ratio', 'value'),
            Output('invest-terms', 'value'),
            Output('age-check', 'value'),
            Output('self-understand-degree', 'value')
        ],
        Input({'type': 'users-dropdown'}, 'value')
    )
    def selected(username):
        if username == 'x':
            return [None]*8
        outputs = user.selections(username)
        # print('-------------outputs----------------')
        # print(outputs)
        for_selected = layout.signup[3]
        values = []
        idx = 0
        for i in range(1, len(for_selected.children), 3):
            values.append(
                for_selected.children[i].options[int(outputs[idx][0]-1)]['value'])
            idx += 1
        # print('-------------values-------------')
        # print(values)
        return values

    def page2_result(content, date, ret, vol):
        if type(content) == str:
            return dcc.ConfirmDialog(
                id='confirm',
                message=content
            )

        table_header = [
            html.Thead(html.Tr([html.Th("시점"), html.Th("Cash"), html.Th(
                "Equity"), html.Th("Fixed Income"), html.Th("Alternative"), html.Th("Total"), html.Th("누적수익률(%)"), html.Th("변동성(%)")]))
        ]

        # print('content.date: {}'.format(content.date))
        # print('date: {}'.format(date))
        latest_content = content.loc[content.date==date, :]
        latest_content.value = to_numeric(latest_content.value)
        # print('content.columns: {}'.format(content.columns))
        # print('content.shape: {}'.format(content.shape))
        # print('content: {}'.format(content))
        # print('----------------------------')
        # print('latest_content.shape: {}'.format(latest_content.shape))
        # print('latest_content.columns: {}'.format(latest_content.columns))
        # print('latest_content: {}'.format(latest_content))
        # print('latest_content.date: {}, date: {}'.format(latest_content.date, date))
        # print('latest_content[latest_content[asset_class] == Cash][value]: {}'.format(latest_content.loc[latest_content.asset_class == 'Cash', 'value']))
        summary = latest_content.loc[:, ['asset_class', 'value']].groupby('asset_class').sum().reset_index()

        total = summary.value.sum()
        total = '{:,}'.format(int(total))

        latest_content.value = latest_content.value.astype(int).apply(lambda x : "{:,}".format(x))
        summary.value = summary.value.astype(int).apply(lambda x : "{:,}".format(x))

        row1 = html.Tr([html.Td("현재"), html.Td(summary.loc[summary.asset_class == 'Cash', 'value']),
                        html.Td(summary.loc[summary.asset_class == 'Equity', 'value']),
                        html.Td(summary.loc[summary.asset_class == 'Fixed Income', 'value']),
                        html.Td(summary.loc[summary.asset_class == 'Alternative', 'value']),
                        html.Td(total),
                        html.Td('{:.1f}'.format(float(ret)*100)),
                        html.Td('{:.1f}'.format(float(vol)*100))
                        # ,
                        # html.Td(html.Div([html.Button('잔고내역보기', id='detail-info-button'),
                        #                   dbc.Modal(
                        #     [
                        #         dbc.ModalHeader("상세 잔고내역"),
                        #         dbc.ModalBody(
                        #             "A small modal.", id='record'),
                        #         dbc.ModalFooter(
                        #             dbc.Button(
                        #                 "Close", id="close-detail-info", className="ml-auto")
                        #         ),
                        #     ],
                        #     id="modal-detail-info",
                        #     size="sm"
                        # )]))
                        ])



        # print('----page2_result에서 상세내역 찍기 시작---')
        # result = user.closeData(select, name=user.name, date=user.date, choice=False)
        # print('content 첫줄 보면..')
        # print(content.iloc[:1, :3])

        result = content
        # RA자문 탭에서 상세잔고내역의 컬럼명/컬럼순서 변경
        result = result.loc[:, ['date', 'name', 'itemname', 'price', 'quantity', 'value', 'cost_price', 'cost_value', 'wt', 'original']]
        result.date = to_datetime(result.date).dt.strftime('%Y-%m-%d')
        result.loc[:, ['price', 'quantity', 'value', 'cost_price', 'cost_value']] = result.loc[:, ['price', 'quantity', 'value', 'cost_price', 'cost_value']].astype(float).astype(int).applymap(lambda x : "{:,}".format(x))
        result.loc[:, ['wt']] = (result.loc[:, ['wt']].astype(float)*100).applymap(lambda x : "{:.1f}".format(x))
        result = result.rename(columns={
            'date':'날짜',
            'name':'이름',
            'itemname': '종목명',
            'price': '종가',
            'quantity': '보유수량',
            'value': '평가금액',
            'cost_price': '매수단가',
            'cost_value': '매수가격',
            'wt': '비중(%)',
            'original': '납입금여부'
        })

        table_header_detail = [
            html.Thead(html.Tr([html.Th(col) for col in list(result.columns)]))
        ]

        rows = result.values.tolist()
        # print(rows)
        table_row = list()
        for row in rows:
            temp = [html.Td(data) for data in row]
            table_row.extend([html.Tr(temp)])


        # row2 = html.Tr([html.Td(""), html.Td(""), html.Td(""), html.Td(""), html.Td(""), html.Td("")])

        # if not content[-1]:
        #     row2.style['background-color'] = '#ddd'
        #     return html.Div(dbc.Table(table_header, html.Tbody([row1, row2]), bordered=True))

        # return html.Div(dbc.Table(table_header + [html.Tbody([row1, row2])], bordered=True))
        return html.Div([dbc.Table(table_header + [html.Tbody([row1])], bordered=True), 
                    dbc.Table(table_header_detail + [html.Tbody(table_row)], bordered=True)])

    def changePeriod(select):
        for idx, sel in enumerate(select):
            if select[idx] < 12:
                select[idx] = (12-select[idx])*30
                continue
            if select[idx] < 14:
                select[idx] = (14-select[idx])*7
                continue
            select[idx] = 17-select[idx]
        return select

    def page3Layout(result, from_date, allowable):
        chart, table = result
        pie = px.pie(
            chart, names=chart['asset_class'].tolist(), values=chart['wt'].tolist())
        fig = dcc.Graph(id='pie-chart-page3')
        fig.figure = pie

        table_header = [
            html.Thead(html.Tr([html.Th("종목명"), html.Th(
                "평가액"), html.Th("비중(%)"), html.Th("자산군")]))
        ]
        informations = table.loc[:, ['itemname', 'value', 'wt', 'asset_class']]
        
        # informations.loc[:, 'wt'] = informations.loc[:, 'wt']*100
        total_value = informations.value.str.replace(',','').astype(float).sum()
        total_value = '{:,}'.format(round(total_value))
        informations.wt = informations.wt.str.replace(',','').astype(float)
        total_wt = informations.wt.sum()
        total_wt = '{:.1f}'.format(float(total_wt))
        informations.wt = informations.wt.apply(lambda x: '{:.1f}'.format(x))


        sumOfInfo = [html.Td('계'), html.Td(total_value), html.Td(total_wt), html.Td('')]
        informations = informations.values.tolist()

        table_row = list()
        for row in informations:
            temp = [html.Td(data) for data in row]
            table_row.extend([html.Tr(temp)])
        table_row.extend([html.Tr(sumOfInfo)])
        table_result = html.Div(
            dbc.Table(table_header + [html.Tbody(table_row)], bordered=True))

        x_axis = [from_date]
        now = from_date
        while now < allowable:
            now += timedelta(days=30)
            x_axis.append(now)
        y_axis = np.random.randn(2, len(x_axis)).tolist()
        y_axis[0].sort()
        y_axis[1].sort()

        # fig_2 = dcc.Graph(id='line-chart')
        # fig_line = go.Figure()
        # fig_line.add_trace(go.Scatter(
        #     x=x_axis, y=y_axis[0], mode='lines+markers', name='before'))
        # fig_line.add_trace(go.Scatter(
        #     x=x_axis, y=y_axis[1], mode='lines+markers', name='after'))
        # fig_2.figure = fig_line

        return html.Div([fig,
                         table_result])

    # def get_next_portfolio(first_trade=False, new_units=None, prices=None, remaining_cash=None):
    #     price_db = PriceDB.instance().data
    #     advised_pf = AdvisedPortfolios.instance().data
    #     risk_profile = 4
    #     current_date = '2021-05-03'

    #     # 시뮬레이션 기간은 현재일(current_date) 다음 날부터 추천 포트폴리오가 존재하는 마지막날까지임.
    #     dates = advised_pf.loc[(advised_pf.risk_profile == risk_profile) & (
    #         advised_pf.date > current_date), 'date'].min()
    #     rebal_dates = dates
    #     print('리밸런싱 일자: ', rebal_dates)

    #     # return할 때 필요한 첫날의 추천 포트 폴리오와 asset class별 정보 수집
    #     new_port = advised_pf.loc[(advised_pf.date == rebal_dates) & (
    #         advised_pf.risk_profile == risk_profile), :]

    #     first_advised_port = new_port.loc[:, ['weights', 'itemname', 'itemcode']].groupby(
    #         ['itemname', 'itemcode']).sum().reset_index()
    #     by_assetclass = new_port.loc[:, ['weights', 'asset_class']].groupby(
    #         'asset_class').sum().sort_values('weights', ascending=False).reset_index()


    #     # next_detail = copy.deepcopy(detail)
    #     next_detail = detail
    #     all_the_nexts = pd.DataFrame(columns=next_detail.columns)
    #     nexts_list = []
    #     price_db = price_db.loc[:, ['date', 'price', 'itemcode']]
    #     price_d = price_db.loc[price_db.date==dt, ['date', 'price', 'itemcode']]

    #     # 리밸런싱한다.
    #     new_port = advised_pf.loc[(advised_pf.risk_profile==risk_profile) & (advised_pf.date==dt), ['date', 'itemcode', 'weights', 'itemname', 'price', 'asset_class']]
    #     next_detail = rebalance(rebal_date=dt, price_d=price_d, detail=next_detail, new_port=new_port)

    #     # all_the_nexts = pd.concat((all_the_nexts, next_detail))
    #     nexts_list.append(next_detail)

    #     all_the_nexts = pd.concat(nexts_list, axis=0)

    #     print('리밸런싱 종료----')
    #     # 불필요한 컬럼 및 행 삭제
    #     all_the_nexts = all_the_nexts.loc[all_the_nexts.quantity > 0]
    #     all_the_nexts = all_the_nexts.reset_index(drop=True)
    #     all_the_nexts['username'] = username

    #     all_the_generals = all_the_nexts.loc[:,['date', 'wt', 'value', 'asset_class']].sort_values(
    #                                     ['date'], ascending=True).groupby([
    #                                         'date', 'asset_class'
    #                                     ]).sum().reset_index(drop=False)
    #     print('자산군별 요약 계산 종료----')

    #     all_the_generals['userid'] = userid

    #     return first_advised_port, by_assetclass, all_the_nexts, all_the_generals

    # def make_comparison(before, after):
    #     before=before.set_index('itemcode', drop=True)
    #     after=after.set_index('itemcode', drop=True)
        
    #     # 매매 전후 테이블 병합 (key: itemcode, which is already set to be the index.)
    #     df_comp = pd.merge(before.loc[:, ['name', 'itemname', 'quantity', 'wt', 'price', 'value']],
    #         after.loc[:, ['itemname', 'quantity', 'wt', 'mp_wt', 'price', 'value']],
    #         left_index=True,
    #         right_index=True,
    #         how='outer',
    #         suffixes=('_before', '_after'))
        
    #     # nan 셀 채우기
    #     df_comp.itemname_before = df_comp.itemname_before.combine_first(after.itemname)
    #     df_comp.itemname_after = df_comp.itemname_after.combine_first(before.itemname)
    #     df_comp.price_after = df_comp.price_after.combine_first(before.price)
    #     df_comp.name = username
    #     df_comp = df_comp.fillna(0)
    #     df_comp = df_comp.assign(quantity_diff= df_comp.quantity_after-df_comp.quantity_before)
        
    #     # 매수/매도 레이블링 조건 정의
    #     conditions = [
    #         df_comp.quantity_diff < 0,
    #         df_comp.quantity_diff == 0,
    #         df_comp.quantity_diff > 0
    #     ]
    #     outputs = ['매도', '-', '매수']
        
    #     df_comp = df_comp.assign(trade=np.select(conditions, outputs))
    #     df_comp = df_comp.assign(quantity_trade=np.abs(df_comp.quantity_diff.astype(int)))
        
    #     # 컬럼명 변경, 컬럼삭제 등 컬럼 정리
    #     df_comp = df_comp.drop(['itemname_after'], axis=1)
    #     df_comp = df_comp.sort_values(by='value_after', ascending=False)
    #     df_comp = df_comp.reset_index()
        
    #     df_comp = df_comp[['name', 'itemcode', 'itemname_before', 'quantity_before', 'wt_before', 'value_before',
    #                 'mp_wt', 'trade', 'quantity_trade', 'quantity_after', 'price_after', 'value_after', 'wt_after']]
        
    #     # 컬럼값 포멧팅(소수점 1자리, 숫자에 컴마 넣기)
    #     df_comp.loc[:, ['mp_wt', 'wt_before', 'wt_after']] = df_comp.loc[:, ['mp_wt', 'wt_before', 'wt_after']]*100
    #     df_comp.loc[:, ['wt_before', 'wt_after']] = df_comp.loc[:, ['wt_before', 'wt_after']].applymap(lambda x: '{:.1f}'.format(x))
    #     df_comp.loc[:, [
    #         'quantity_before', 'wt_before', 'value_before', 'quantity_after',
    #         'price_after', 'value_after'
    #     ]] = df_comp.loc[:, [
    #         'mp_wt', 'quantity_before', 'wt_before', 'value_before', 'quantity_after',
    #         'price_after', 'value_after'
    #     ]].astype(float).astype(int).applymap(lambda x: '{:,}'.format(x))

    #     # 컬럼명 한글로
    #     df_comp = df_comp.rename(columns = {
    #         'name':'이름',
    #         'itemcode':'종목코드',
    #         'itemname_before':'종목명',
    #         'quantity_before':'수량(전)',
    #         'wt_before':'비중(전)',
    #         'value_before':'평가액(전)',
    #         'mp_wt':'MP비중',
    #         'trade':'매매방향',
    #         'quantity_trade':'매매수량',
    #         'quantity_after':'수량(후)',
    #         'price_after':'가격(후)',
    #         'value_after':'평가액(후)',
    #         'wt_after':'비중(후)'
    #     })
        
    #     return df_comp

    @app.callback(
        [Output('output-pos', 'children'),
         Output('max-date', 'children')],
        Input('predict-slider', 'value'),
        Input({'type': 'filter-dropdown'}, 'value')
    )
    def show_prediction(select, name):
        user.name = name
        print('in show_prediction, name is {}'.format(name))
        date = user.getStartDate(name)
        # print('app.py show_prediction params: date {}, name {}, select {}'.format(date, name, select))
        user.date = date
        select = changePeriod(select)
        # result는 DataFrame 타입임.

        ## 리밸런싱 전후 비교 코드 시작 ----
#        df_comp = make_comparison(before, after)

        result = user.closeData(select, date, name, choice=True)
        ret, vol = user.getPerformance(name)
        # print('return: {}, vol: {}'.format(ret, vol))
        # print('-----result of closeData---- result type is: {}'.format(type(result)))
        # print(result)
        return page2_result(result, date, ret, vol), date

    @app.callback(
        Output('modal-detail-info', 'is_open'),
        Output('record', 'children'),
        [Input('detail-info-button', 'n_clicks'),
            Input('close-detail-info', 'n_clicks')],
        State('modal-detail-info', 'is_open'),
        State('predict-slider', 'value')
    )
    def detailInfo(open, close, is_open, select):
        # print('----in detailInfo. close: {}, is_open: {}, select is {}'.format(close, is_open, select))
        select = changePeriod(select)
        # print('After-{}'.format(select))
        # print('user.name: {}'.format(user.name))
        # print('user.date: {}'.format(user.date))
        result = user.closeData(select, name=user.name, date=user.date, choice=False)
        # print('여기랑 이름이 같아야..')
        # print(result.iloc[:1, :3])

        # RA자문 탭에서 상세잔고내역의 컬럼명/컬럼순서 변경
        result = result.loc[:, ['date', 'name', 'itemname', 'price', 'quantity', 'value', 'cost_price', 'cost_value', 'wt', 'original']]
        result.date = to_datetime(result.date).dt.strftime('%Y-%m-%d')
        result.loc[:, ['price', 'quantity', 'value', 'cost_price', 'cost_value']] = result.loc[:, ['price', 'quantity', 'value', 'cost_price', 'cost_value']].astype(float).astype(int).applymap(lambda x : "{:,}".format(x))
        result.loc[:, ['wt']] = (result.loc[:, ['wt']].astype(float)*100).applymap(lambda x : "{:.1f}".format(x))
        result = result.rename(columns={
            'date':'날짜',
            'name':'이름',
            'itemname': '종목명',
            'price': '종가',
            'quantity': '보유수량',
            'value': '평가금액',
            'cost_price': '매수단가',
            'cost_value': '매수가격',
            'wt': '비중(%)',
            'original': '납입금여부'
        })

        table_header = [
            html.Thead(html.Tr([html.Th(col) for col in list(result.columns)]))
        ]

        rows = result.values.tolist()
        # print(rows)
        table_row = list()
        for row in rows:
            temp = [html.Td(data) for data in row]
            table_row.extend([html.Tr(temp)])

        result = html.Div(
            dbc.Table(table_header + [html.Tbody(table_row)], bordered=True))
        if open or not close:
            return not is_open, result
        return is_open, result

    @app.callback(
        Output('info-datetime', 'value'),
        Input({'type': 'filter-dropdown'}, 'value'),
    )
    def page3DateResult(name):
        user.name = name
        startPoint = user.getStartDate(name)
        return startPoint

    @app.callback(
        Output('detail-info-output', 'children'),
        [Input('default-predict-date', 'date'),
         Input({'type': 'filter-dropdown'}, 'value')]
    )
    def page3OutputResult(pDate, userchoice):
        try:
            temp = pDate.split('-')
            pDate = temp[1]+'/'+temp[2]+'/'+temp[0]+' 4:00:00 PM'
        except:
            pDate += ' 4:00:00 PM'
        user.name = userchoice

        print('in page3OutputResult(), user.date is {}'.format(user.date))
        print('Selected date: {}'.format(pDate))
        result = user.page3Data(pDate)

        return page3Layout(result, datetime.strptime(pDate, '%m/%d/%Y %I:%M:%S %p'), datetime.strptime(pDate, '%m/%d/%Y %I:%M:%S %p'))


show_content(user)

if __name__ == '__main__':
    app.run_server(debug=True)
