import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import json
import os

with open(os.getcwd() + '/Styles.json', 'rb') as f:
    style = json.load(f)

tabs_styles, tab_style, tab_selected_style = style['tabs_styles'], style['tab_style'], style['tab_selected_style']
output_id = 'tabs-content-inline'
input_id = "tabs-styled-with-inline"

signup = html.Div([
    html.Div([
        html.Label('이름'),
        dcc.Input(value=None, type='text', id='name'),

        html.Label('날짜'),
        dcc.Input(value=None, type='text', id='datetime'),

        html.Label('투자금액'),
        dcc.Input(value=None, type='text', id='invest-scale')]

        , id='user-information'),

    html.Hr(style={"width": "3000px"}),

    html.Div([
        html.Label('1. 투자경험'),
        dcc.RadioItems(
            options=[
                {'label': "없음", "value": "no-experience"},
                {'label': "6개월 이하", "value": "6-months"},
                {'label': "1년 이하", "value": "1-year"},
                {'label': "2년 이하", "value": "2-year"},
                {'label': "2년 초과", "value": "over 2-year"}
            ], value=None,
            labelStyle={'display': 'inline-block', 'width': '20%', 'margin': 'auto', 'marginTop': 15,
                        'paddingLeft': 15},
            id='invest-experience'
        ),

        html.Hr(style={"width": "3000px"}),

        html.Label('2. 투자목적', ),

        dcc.RadioItems(
            options=[
                {'label': "원금손실 위험 조금만 감수하고 예금을 살짝 웃도는 수익", "value": "little"},
                {'label': "원금손실 위험 감내하고 투자수익 추구", "value": "medium"},
                {'label': "원금손실 위험 적극 감내하고 고수익 추구", "value": "high"}
            ], value=None,
            labelStyle={'display': 'inline-block', 'width': '20%', 'margin': 'auto', 'marginTop': 15,
                        'paddingLeft': 15},
            id='invest-purpose'
        ),
        html.Hr(style={"width": "3000px"}),

        html.Label('3. 투자기간 중 감내 가능한 투자 손실액'),
        dcc.RadioItems(
            options=[
                {'label': "감내불가(0%)", "value": "zero"},
                {'label': "5%이하", "value": "five"},
                {'label': "10%이하", "value": "ten"},
                {'label': "20%이하", "value": "twenty"},
                {'label': "20%초과", "value": "over-twenty"},
            ], value=None,
            labelStyle={'display': 'inline-block', 'width': '20%', 'margin': 'auto', 'marginTop': 15,
                        'paddingLeft': 15},
            id='character-risk'
        ),
        html.Hr(style={"width": "3000px"}),

        html.Label('4. 연간소득'),
        dcc.RadioItems(
            options=[
                {'label': "3000만원 이하", "value": "three-thousand"},
                {'label': "6000만원 이하", "value": "six-thousand"},
                {'label': "1억 이하", "value": "one-billion"},
                {'label': "2억 이하", "value": "two-billion"},
                {'label': "2억 초과", "value": "over-two-billion"}
            ], value=None,
            labelStyle={'display': 'inline-block', 'width': '20%', 'margin': 'auto', 'marginTop': 15,
                        'paddingLeft': 15},
            id='annual-income'
        ),
        html.Hr(style={"width": "3000px"}),

        html.Label('5. 금융자산의 비중'),
        dcc.RadioItems(
            options=[
                {'label': "순자산의 5%이하", "value": "lower-five"},
                {'label': "10%이하", "value": "lower-ten"},
                {'label': "20%이하", "value": "lower-twenty"},
                {'label': "30%이하", "value": "lower-thirty"},
                {'label': "30%초과", "value": "over-thirty"}
            ], value=None,
            labelStyle={'display': 'inline-block', 'width': '20%', 'margin': 'auto', 'marginTop': 15,
                        'paddingLeft': 15},
            id='finance-ratio'
        ),
        html.Hr(style={"width": "3000px"}),

        html.Label('6. 투자 기간'),
        dcc.RadioItems(
            options=[
                {'label': "1년 이하", "value": "below-one-year"},
                {'label': "3년 이하", "value": "below-three-year"},
                {'label': "5년 이하", "value": "below-five-year"},
                {'label': "5년 초과", "value": "over-five-year"},
            ], value=None,
            labelStyle={'display': 'inline-block', 'width': '20%', 'margin': 'auto', 'marginTop': 15,
                        'paddingLeft': 15},
            id='invest-terms'
        ),
        html.Hr(style={"width": "3000px"}),

        html.Label('7. 연령대'),
        dcc.RadioItems(
            options=[
                {'label': "10대 미만", "value": "below-teenage"},
                {'label': "10대", "value": "teenage"},
                {'label': "20대", "value": "two-age"},
                {'label': "30대", "value": "three-age"},
                {'label': "40대", "value": "four-age"},
                {'label': "50대", "value": "five-age"},
                {'label': "60대 이상", "value": "six-age"}
            ], value=None,
            labelStyle={'display': 'inline-block', 'width': '20%', 'margin': 'auto', 'marginTop': 15,
                        'paddingLeft': 15},
            id='age-check'
        ),
        html.Hr(style={"width": "3000px"}),

        html.Label('8. 투자상품 이해에 대한 자기평가'),
        dcc.RadioItems(
            options=[
                {'label': "원금손실 가능한 투자상품 경험 없음", "value": "no-invest"},
                {'label': "ELS 투자경험", "value": "ELS"},
                {'label': "펀드나 ETF투자경험", "value": "fund"},
                {'label': "주식 투자경험", "value": "stock"},
            ], value=None,
            labelStyle={'display': 'inline-block', 'width': '20%', 'margin': 'auto', 'marginTop': 15,
                        'paddingLeft': 15},
            id='self-understand-degree'
        )
    ], id='check-list'),

    html.Br(),
    html.Br(),
    html.Button('Submit', id='submit-val', style={"background-color": "Yellow"}, n_clicks=0),
    html.Div([
        html.Div(id='character-result'),
    ], id='output-div')

    ], style={'visibility': "hidden"}
)

analysis = html.Div([
    html.Div([
        html.Label('이름'),
        dcc.Input(value='x', type='text', id='analysis-name'),

        html.Label('날짜'),
        dcc.Input(value='y', type='text', id='analysis-datetime')]

        , id='user-information-analysis'),

    dcc.Slider(
        id='predict-slider',
        min=0,
        max=16,
        value=0,
        marks={
            0: {'label': '1일'},
            1: {'label': '2일'},
            2: {'label': '3일'},
            3: {'label': '1주'},
            4: {'label': '2주'},
            5: {'label': '1개월'},
            6: {'label': '2개월'},
            7: {'label': '3개월'},
            8: {'label': '4개월'},
            9: {'label': '5개월'},
            10: {'label': '6개월'},
            11: {'label': '7개월'},
            12: {'label': '8개월'},
            13: {'label': '9개월'},
            14: {'label': '10개월'},
            15: {'label': '11개월'},
            16: {'label': '12개월'},
        }
    ),
    html.Div(id='output-pos')
    ],
    style={"visibility": "hidden"}, id='analysis'
)

tab = html.Div([
    dcc.Tabs(id=input_id, value='signup', children=[
        dcc.Tab(label='가입', value='signup', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='RA자문', value='analysis', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='투자내역', value='info', style=tab_style, selected_style=tab_selected_style)
    ], style=tabs_styles),
    html.Div([signup, analysis], id=output_id, style={'display':'none'})
])