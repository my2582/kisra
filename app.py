import dash
import dash_html_components as html
from character import Character
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import layout
from data import Data
from user import User
import numpy as np
from datetime import timedelta, datetime
import plotly.graph_objects as go
from DataBase import databaseDF
from src.models.load_data import AdvisedPortfolios, Singleton, PriceDB
from skimage import io
from pandas import to_numeric, to_datetime
import pandas as pd
import copy
from pypfopt.discrete_allocation import DiscreteAllocation

sheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=sheet,
                suppress_callback_exceptions=True,
                prevent_initial_callbacks=True)
server = app.server

def show_content():
    style = layout.style
    user = User()
    # global _user
    app.layout = html.Div(layout.main_login, id='main-layout')
    check = False

    # 3번째 탭용 테스트 데이터 세팅
    # risk_profile = 4
    # current_date = '2021-06-01'
    # userid = 'A001'
    # username = '안정추구형소규모'

    db = databaseDF()
    # advised_pf = AdvisedPortfolios.instance().data
    # print('type(advised_pf)'.format(type(advised_pf)))
    # print('Here is your advised_pf:')
    # print(advised_pf.tail(3))
    # db.insert_advised_pf(advised_pf)

    @app.callback(
        Output('main-layout', 'children'),
        [Input('login-button', 'n_clicks'),
         Input('sign-up-button', 'n_clicks')],
        State('user-id-main', 'value')
    )
    def show_layout(login, signup, user_id):
        user = User(userid=user_id)
        user.date = '8/31/2021 4:00:00 PM'
        # if user.name:
        #     user.name = ""
        #     user.userid = ""
        #     user.data = Data()
        #     user.date = ""

        print('#1. in show_layout, login: {}, signup: {}, user_id: {}'.format(login, signup, user_id))
        if 0 < login:
            temp = copy.deepcopy(layout.tab)
            temp.children[0].children = temp.children[0].children[1:]
            temp.children[0].value = 'analysis'
            # user.name = copy.deepcopy(user_id)
            print('#3. in show_layout, login: {}, signup: {}, user.name: {}, user_id: {}'.format(login, signup, user.name, user_id))
            # layout.main_login.children[2].n_clicks = 0
            layout.main_login.children[2].n_clicks = 0
            check = False
            return temp
        if 0 < signup:
            layout.main_login.children[5].n_clicks = 0
            check = True
            layout.tab.children[0].value = 'signup'
            return layout.tab
        
        print('login and signup >= 0!! Despite of this, let me set user.name to be user_id {}.'.format(user.name))
        return layout.main_login

    @app.callback(
        Output(layout.output_id, 'children'),
        Input(layout.input_id, 'value')
    )
    def show_page(tab_input):
        # global _user
        if tab_input == 'signup':
            return html.Div(layout.signup)

        if tab_input == 'analysis':
            if not check:
                # 로그인을 했을 경우
                # RA자문 탭의 이름과 자문기준일 값을 설정함.
                layout.analysis[0].children[1].children = ''
                layout.analysis[0].children[3].children = '8/31/2021 4:00:00 PM'
                # layout.analysis[0].children[3].children = user.getStartDate(user.name)
            # layout.analysis[0].children[1].children = user.name
            # layout.analysis[0].children[3].children = '6/2/2021 4:00:00 PM'
            
            # 처음 로그인할 때 이게 user.name이 none이었음.
            # 다른 브라우저로 다른 아이디로 로그인할 때는 이 값이 사용자가 입력한 값을 가짐.
            # 세 번째 로그인도 잘 작동.
            # 네 번째 로그인도 잘 작동.

            # 관찰결과: user.name에 한 세션 이전의 사용자명이 저장되어 있음.
            # print('This is user.name: {}'.format(user.name))

            return html.Div(layout.analysis)

        if tab_input == 'info':
            if not check:
                # 로그인을 했을 경우
                layout.info[0].children[1].children = copy.deepcopy(user.name)
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
            user.name = input_11
            user.date = input_10
            print(user.name, user.date)
            character = Character(tags_id)
            # print('tags_id: {}'.format(tags_id))
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
                for n in range(0, len(layout.signup)):
                    print('layout.signup[{}]: {}'.format(n, layout.signup[n]))

                for_selected = layout.signup[2]   # 투자자 성향분석 선택지값들.
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
                # rpt_url = 'https://raw.githubusercontent.com/my2582/kisra_storage/main/report-{}_{}.png'.format(risk_profile, current_date)
                # rpt2_url = 'https://raw.githubusercontent.com/my2582/kisra_storage/main/ef_area-{}_{}.png'.format(risk_profile, current_date)
                # rpt3_url = 'https://raw.githubusercontent.com/my2582/kisra_storage/main/ef-{}_{}.png'.format(risk_profile, current_date)
                # print('URLs:', rpt_url, rpt2_url, rpt3_url)
                # fig_rpt = get_fig(source=rpt_url, width=1008, height=2592)
                # fig_rpt2 = get_fig(source=rpt2_url, width=1000, height=600)
                # fig_rpt3 = get_fig(source=rpt3_url, width=640, height=480)
                
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
                # output.children.append(dcc.Graph(id="fig-image", figure=fig_rpt, config={'doubleClick': 'reset'}))
                # output.children.append(dcc.Graph(id="fig2-image", figure=fig_rpt2, config={'doubleClick': 'reset'}))
                # output.children.append(dcc.Graph(id="fig3-image", figure=fig_rpt3, config={'doubleClick': 'reset'}))
                return output

            warning = '비어있는 항목이 있습니다! 전부 체크해 주세요'
            if 2 < len(output.children):
                output.children = output.children[:-1]
            output.children[0].children = warning
            output.style = style['pie_chart_style']
            return output

    def page2_result(content, date, ret, vol, df_comp):
        if type(content) == str:
            return dcc.ConfirmDialog(
                id='confirm',
                message=content
            )

        table_title1 = [html.Thead(html.Tr([html.H4("리밸런싱 전/후 비교")]))]
        table_title2 = [html.Thead(html.Tr([html.H4("자산별 구성 및 운용성과")]))]
        table_title3 = [html.Thead(html.Tr([html.H4("리밸런싱 과거 내역")]))]

        table_header_comp = [

            html.Thead(html.Tr([html.Th(col) for col in list(df_comp.columns)]))
        ]

        print('table_header_comp is : {}'.format(table_header_comp))
        print('in page2_result, df_comp is', df_comp)
        rows = df_comp.values.tolist()
        # print(rows)
        comp_row = list()
        for row in rows:
            temp = [html.Td(record) for record in row]
            comp_row.extend([html.Tr(temp)])

        print('in page2_result, comp_row is', comp_row)


        table_header = [
            html.Thead(html.Tr([html.Th("시점"), html.Th("Cash"), html.Th(
                "Equity"), html.Th("Fixed Income"), html.Th("Alternative"), html.Th("Total"), html.Th("누적수익률(%)"), html.Th("변동성(%)")]))
        ]

        # print('content.date: {}'.format(content.date))
        # print('date: {}'.format(date))
        latest_content = content.loc[content.date==date, :]
        latest_content.value = to_numeric(latest_content.value)
        print('content.columns: {}'.format(content.columns))
        print('content.shape: {}'.format(content.shape))
        print('content: {}'.format(content))
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
                        ])



        # print('----page2_result에서 상세내역 찍기 시작---')
        # result = user.closeData(select, name=user.name, date=user.date, choice=False)
        # print('content 첫줄 보면..')
        # print(content.iloc[:1, :3])

        # 과거 내역(detail) 중 리밸런싱이 발생한 날짜의 레코드만
        result = content.loc[content.original == 'Rebal', :]
        print('content.shape: {}, result.shape: {}'.format(content.shape, result.shape))
        
        # RA자문 탭에서 상세잔고내역의 컬럼명/컬럼순서 변경
        result = result.loc[:, ['date', 'name', 'itemname', 'price', 'quantity', 'value', 'wt', 'original']]
        result.date = to_datetime(result.date).dt.strftime('%Y-%m-%d')
        result.loc[:, ['price', 'quantity', 'value']] = result.loc[:, ['price', 'quantity', 'value']].astype(float).astype(int).applymap(lambda x : "{:,}".format(x))
        result.loc[:, ['wt']] = (result.loc[:, ['wt']].astype(float)*100).applymap(lambda x : "{:.1f}".format(x))
        result = result.rename(columns={
            'date':'날짜',
            'name':'이름',
            'itemname': '종목명',
            'price': '종가',
            'quantity': '보유수량',
            'value': '평가금액',
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

        print('table_header_detail is {}'.format(table_header_detail))
        print('in page2_result, table_row is', table_row)

        return html.Div([dbc.Table(table_title1, bordered=False, style = {'margin-top' : '18px',
                            'margin-bottom' : '10px',
                            'text-align' : 'left',
                            'paddingLeft': 12}),
                    dbc.Table(table_header_comp + [html.Tbody(comp_row)], bordered=True, style = {'margin-top' : '18px',
                            'margin-bottom' : '10px',
                            'text-align' : 'left',
                            'paddingLeft': 12}),
                    dbc.Table(table_title2, bordered=False, style = {'margin-top' : '18px',
                            'margin-bottom' : '10px',
                            'text-align' : 'left',
                            'paddingLeft': 12}),
                    dbc.Table(table_header + [html.Tbody([row1])], bordered=True, style = {'margin-top' : '18px',
                            'margin-bottom' : '10px',
                            'text-align' : 'left',
                            'paddingLeft': 12}),
                    dbc.Table(table_title3, bordered=False, style = {'margin-top' : '18px',
                            'margin-bottom' : '10px',
                            'text-align' : 'left',
                            'paddingLeft': 12}),
                    dbc.Table(table_header_detail + [html.Tbody(table_row)], bordered=True, style = {'margin-top' : '18px',
                            'margin-bottom' : '10px',
                            'text-align' : 'left',
                            'paddingLeft': 12})])

        # return html.Div([dbc.Table(table_title1, bordered=False),
        #             dbc.Table(table_header_comp + [html.Tbody(comp_row)], bordered=True), 
        #             dbc.Table(table_title3, bordered=False),
        #             dbc.Table(table_header_detail + [html.Tbody(table_row)], bordered=True)])


        # return html.Div([dbc.Table(table_title1, bordered=False),
        #             dbc.Table(table_header_comp + [html.Tbody(comp_row)], bordered=True), 
        #             dbc.Table(table_title3, bordered=False),
        #             dbc.Table(table_header_detail + [html.Tbody(table_row)], bordered=True)])

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
        print('chart: {}, chart.keys(): {}'.format(chart, chart.keys()))
        print('table: {}'.format(table))
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

    def rebalance(rebal_date, price_d, detail, new_port):
        '''
        Rebalance a portfolio.

        Parameters:
        rebal_date: str
            rebalancing date

        detail: DataFrame
        current balance

        price_d: DataFrame
        price data on rebal_date

        new_port: DataFrame
        A new portfolio. Your current portfolio in `detail` will be rebalanced toward `new_port`.
        '''
        trading_amt = detail.value.sum()       

        wt = new_port[['itemcode', 'weights']].set_index('itemcode').to_dict()['weights']
        pr = new_port[['itemcode', 'price']].set_index('itemcode').squeeze()

        da = DiscreteAllocation(weights=wt, latest_prices=pr, total_portfolio_value=trading_amt)

        allocation, remaining_cash = da.greedy_portfolio()
        print("리밸런싱 결과:")
        print("{}: 새 포트폴리오(종목코드:수량)-{}".format(rebal_date,allocation))
        print(" - 매매 후 잔액: {:.2f} KRW".format(remaining_cash))

        # 매매한 뒤의 레코드 생성
        df_qty = pd.DataFrame.from_dict(allocation, orient='index', columns=['quantity'])
        next_detail = new_port.merge(df_qty, left_on='itemcode', right_index=True, how='inner')
        next_detail['cost_price'] = next_detail.price.copy()   
        next_detail['cost_value'] = next_detail.cost_price*next_detail.quantity
        next_detail['value'] = next_detail.cost_value.copy()

        # 매매하고 남은 돈은 현금으로
        df_cash = {
            'itemcode': 'C000001',
            'quantity': remaining_cash,
            'cost_price': 1,
            'price':1,
            'cost_value': remaining_cash,
            'value': remaining_cash,
            'itemname': '현금',
            'asset_class': 'Cash'
        }
        df_cash = pd.DataFrame.from_dict(df_cash, orient='index').T

        next_detail = pd.concat((next_detail[['itemcode', 'quantity', 'cost_price', 'price', 'cost_value', 'value',
        'itemname', 'asset_class']], df_cash), axis=0)

        next_detail['wt'] = next_detail.value/next_detail.value.sum()
        next_date = datetime.strptime(rebal_date, '%Y-%m-%d')
        #next_date = str(next_date.month)+'/'+str(next_date.day)+'/'+str(next_date.year)+' 03:30:00 PM'
        next_detail['date'] = next_date
        next_detail.reset_index(drop=True, inplace=True)
        next_detail['group_by'] = ''
        next_detail = pd.merge(next_detail,
                price_d.loc[price_d.date==rebal_date, ['date', 'itemcode']],
                left_on=['date', 'itemcode'],
                right_on=['date', 'itemcode'], how='left')
        next_detail['username'] = username
        next_detail['userid'] = userid
        next_detail['original'] = 'Rebal'
        next_detail = next_detail.rename(columns={'weights':'wt'})
        next_detail = next_detail[['itemcode', 'quantity', 'cost_price', 'price', 'cost_value', 'value',
            'itemname', 'asset_class', 'date', 'userid', 'username', 'group_by',
            'original', 'wt']]

        return next_detail

    def get_next_portfolio(first_trade=False, new_units=None, prices=None, remaining_cash=None, detail=None):
        price_db = PriceDB.instance().data
        advised_pf = AdvisedPortfolios.instance().data

        # 시뮬레이션 기간은 현재일(current_date) 다음 날부터 추천 포트폴리오가 존재하는 마지막날까지임.
        dates = advised_pf.loc[(advised_pf.risk_profile == risk_profile) & (
            advised_pf.date > current_date), 'date'].min()
        rebal_dates = dates
        dt = rebal_dates     # dt랑 rebal_dates, dates 다 똑같음. 
        print('리밸런싱 일자: ', rebal_dates)

        # return할 때 필요한 첫날의 추천 포트 폴리오와 asset class별 정보 수집
        new_port = advised_pf.loc[(advised_pf.date == rebal_dates) & (
            advised_pf.risk_profile == risk_profile), :]

        first_advised_port = new_port.loc[:, ['weights', 'itemname', 'itemcode']].groupby(
            ['itemname', 'itemcode']).sum().reset_index()
        by_assetclass = new_port.loc[:, ['weights', 'asset_class']].groupby(
            'asset_class').sum().sort_values('weights', ascending=False).reset_index()


        # next_detail = copy.deepcopy(detail)
        next_detail = detail
        all_the_nexts = pd.DataFrame(columns=next_detail.columns)
        nexts_list = []
        price_db = price_db.loc[:, ['date', 'price', 'itemcode']]
        price_d = price_db.loc[price_db.date==dt, ['date', 'price', 'itemcode']]

        # 리밸런싱한다.
        new_port = advised_pf.loc[(advised_pf.risk_profile==risk_profile) & (advised_pf.date==dt), ['date', 'itemcode', 'weights', 'itemname', 'price', 'asset_class']]
        next_detail = rebalance(rebal_date=dt, price_d=price_d, detail=next_detail, new_port=new_port)

        # all_the_nexts = pd.concat((all_the_nexts, next_detail))
        nexts_list.append(next_detail)

        all_the_nexts = pd.concat(nexts_list, axis=0)

        print('리밸런싱 종료----')
        # 불필요한 컬럼 및 행 삭제
        all_the_nexts = all_the_nexts.loc[all_the_nexts.quantity > 0]
        all_the_nexts = all_the_nexts.reset_index(drop=True)
        all_the_nexts['username'] = username

        all_the_generals = all_the_nexts.loc[:,['date', 'wt', 'value', 'asset_class']].sort_values(
                                        ['date'], ascending=True).groupby([
                                            'date', 'asset_class'
                                        ]).sum().reset_index(drop=False)
        print('자산군별 요약 계산 종료----')

        all_the_generals['userid'] = userid

        return first_advised_port, by_assetclass, all_the_nexts, all_the_generals

    def make_comparison(before, after):
        before=before.set_index('itemcode', drop=True)
        after=after.set_index('itemcode', drop=True)
        
        # 매매 전후 테이블 병합 (key: itemcode, which is already set to be the index.)
        df_comp = pd.merge(before.loc[:, ['name', 'itemname', 'quantity', 'wt', 'price', 'value']],
            after.loc[:, ['itemname', 'quantity', 'wt', 'mp_wt', 'price', 'value']],
            left_index=True,
            right_index=True,
            how='outer',
            suffixes=('_before', '_after'))
        
        # nan 셀 채우기
        df_comp.itemname_before = df_comp.itemname_before.combine_first(after.itemname)
        df_comp.itemname_after = df_comp.itemname_after.combine_first(before.itemname)
        df_comp.price_after = df_comp.price_after.combine_first(before.price)
        df_comp.name = username
        df_comp = df_comp.fillna(0)
        df_comp = df_comp.assign(quantity_diff= df_comp.quantity_after-df_comp.quantity_before)
        
        # 매수/매도 레이블링 조건 정의
        conditions = [
            df_comp.quantity_diff < 0,
            df_comp.quantity_diff == 0,
            df_comp.quantity_diff > 0
        ]
        outputs = ['매도', '-', '매수']
        
        df_comp = df_comp.assign(trade=np.select(conditions, outputs))
        df_comp = df_comp.assign(quantity_trade=np.abs(df_comp.quantity_diff.astype(int)))
        
        # 컬럼명 변경, 컬럼삭제 등 컬럼 정리
        df_comp = df_comp.drop(['itemname_after'], axis=1)
        df_comp = df_comp.sort_values(by='value_after', ascending=False)
        df_comp = df_comp.reset_index()
        
        df_comp = df_comp[['name', 'itemcode', 'itemname_before', 'quantity_before', 'wt_before', 'value_before',
                    'mp_wt', 'trade', 'quantity_trade', 'quantity_after', 'price_after', 'value_after', 'wt_after']]
        
        # 컬럼값 포멧팅(소수점 1자리, 숫자에 컴마 넣기)
        df_comp.loc[:, ['mp_wt', 'wt_before', 'wt_after']] = df_comp.loc[:, ['mp_wt', 'wt_before', 'wt_after']]*100
        df_comp.loc[:, ['mp_wt', 'wt_before', 'wt_after']] = df_comp.loc[:, ['mp_wt', 'wt_before', 'wt_after']].applymap(lambda x: '{:.1f}'.format(x))
        df_comp.loc[:, [
            'quantity_before', 'value_before', 'quantity_after',
            'price_after', 'value_after'
        ]] = df_comp.loc[:, [
            'quantity_before', 'value_before', 'quantity_after',
            'price_after', 'value_after'
        ]].astype(float).astype(int).applymap(lambda x: '{:,}'.format(x))

        # 컬럼명 한글로
        df_comp = df_comp.rename(columns = {
            'name':'이름',
            'itemcode':'종목코드',
            'itemname_before':'종목명',
            'quantity_before':'수량(전)',
            'wt_before':'비중(전)',
            'value_before':'평가액(전)',
            'mp_wt':'MP비중',
            'trade':'매매방향',
            'quantity_trade':'매매수량',
            'quantity_after':'수량(후)',
            'price_after':'가격(후)',
            'value_after':'평가액(후)',
            'wt_after':'비중(후)'
        })
        
        return df_comp

    @app.callback(
        [Output('output-pos', 'children'),
         Output('max-date', 'children')],
        Input('predict-slider', 'value')
    )
    def show_prediction(select):

        '''
        user.name: 로그인 시 입력한 사용자 이름을 갖고 있음
        user.userid: null. not available here.
        '''
        # global _user

        # user.name = username
        # user.userid = userid

        # 안정추구형중규모로 접속 시 -> user.name이 이전 세션 값이다. 
        # 안정추구형대규모로 접속 시 -> 정상
        print('app.py show_prediction params: user.date {}, user.userid {}, user.name {}'.format(user.date, user.userid, user.name))

        # userid를 얻는다.
        user_list = db.getUserList()

        # user_list가 (userid, name) 순으로 되어 있어서, 이 순서를 바꿔서 딕셔너리를 만든다(key가 name이 되도록 한다)
        user_dict = user_dict = {u[1]: u[0] for u in user_list}
        user.userid = user_dict[user.name]
        select = changePeriod(select)

        df_comp_pkl = pd.read_pickle('./data/processed/comparison_0901_{}.pkl'.format(user.userid))
        print('리밸런싱 전/후 비교(1):', df_comp_pkl)

        # # 최근 잔고 가져옴
        # detail = db.getUserBalance(userid=userid)       
        # detail = pd.DataFrame(detail, columns=['date', 'userid', 'name', 'asset_class', 'itemcode', 'itemname',
        #                                         'quantity', 'cost_price', 'cost_value', 'price', 'value', 'wt', 'group_by', 'original'])

        # # 리밸런싱 후 포트폴리오 가져오기
        # first_advised_port, by_assetclass, all_the_nexts, all_the_generals = get_next_portfolio(detail=detail)
        
        # # 리밸런싱 전후 비교 테이블 생성
        # before = detail
        # after = all_the_nexts
        # after = after.merge(first_advised_port.loc[:, ['itemcode', 'weights']], left_on='itemcode', right_on='itemcode', how='left')
        # after.weights = after.weights.fillna(0)
        # after = after.rename(columns={'weights':'mp_wt'})
        # df_comp = make_comparison(before, after)

        # print('리밸런싱 전/후 비교(2):', df_comp)

        # result는 DataFrame 타입임.
        result = user.closeData(select, user.date, user.name, choice=True)
        ret, vol = user.getPerformance(user.name)
        print('return: {}, vol: {}'.format(ret, vol))
        print('-----result of closeData---- result type is: {}'.format(type(result)))
        print(result)
        return page2_result(result, user.date, ret, vol, df_comp_pkl), user.date

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
        Output('detail-info-output', 'children'),
        [Input('default-predict-date', 'date')]
    )
    def page3OutputResult(pDate):
        try:
            temp = pDate.split('-')
            pDate = temp[1]+'/'+temp[2]+'/'+temp[0]+' 4:00:00 PM'
        except:
            pDate += ' 4:00:00 PM'
        
        print('Selected date: {}'.format(pDate))
        print(user.name)
        result = user.page3Data(pDate)

        return page3Layout(result, datetime.strptime(pDate, '%m/%d/%Y %I:%M:%S %p'), datetime.strptime(pDate, '%m/%d/%Y %I:%M:%S %p'))


# _user is a global variable. This name is changed from user for less confusion.
show_content()

if __name__ == '__main__':
    # app.secret_key = 'sgoijio3221SIkldOIDs'
    app.run_server(debug=True)
