import dash_html_components as html
import dash_core_components as dcc
import User

class SignUp:

    def __init__(self):
        self.user = User.User()

    def layout(self):

        layout = [
            html.Div([
                html.Label('이름'),
                dcc.Input(value='name', type='text', id = 'name'),

                html.Label('날짜'),
                dcc.Input(value='date', type='text', id = 'datetime'),

                html.Label('투자금액'),
                dcc.Input(value='money', type='text', id = 'invest-scale')]

            , id = 'user-information'),

            html.Hr(style={"width" : "3000px"}),

            html.Div([
                html.Label('1. 투자경험'),
                dcc.RadioItems(
                    options = [
                        {'label' : "없음", "value" : "no-experience"},
                        {'label' : "6개월 이하", "value" : "6-months"},
                        {'label' : "1년 이하", "value" : "1-year"},
                        {'label' : "2년 이하", "value" : "2-year"},
                        {'label' : "2년 초과", "value" : "over 2-year"}
                    ], value = 'experience',
                    labelStyle={'display': 'inline-block', 'width': '20%', 'margin':'auto', 'marginTop': 15, 'paddingLeft': 15},
                    id = 'invest-experience'
                ),

                html.Hr(style={"width" : "3000px"}),

                html.Label('2. 투자목적', ),

                dcc.RadioItems(
                    options = [
                        {'label' : "원금손실 위험 조금만 감수하고 예금을 살짝 웃도는 수익", "value" : "little"},
                        {'label' : "원금손실 위험 감내하고 투자수익 추구", "value" : "medium"},
                        {'label' : "원금손실 위험 적극 감내하고 고수익 추구", "value" : "high"}
                    ], value = 'purpose',
                    labelStyle={'display': 'inline-block', 'width': '20%', 'margin':'auto', 'marginTop': 15, 'paddingLeft': 15},
                    id = 'invest-purpose'
                ),
                html.Hr(style={"width" : "3000px"}),

                html.Label('3. 투자기간 중 감내 가능한 투자 손실액'),
                dcc.RadioItems(
                    options = [
                        {'label' : "감내불가(0%)", "value" : "zero"},
                        {'label' : "5%이하", "value" : "five"},
                        {'label' : "10%이하", "value" : "ten"},
                        {'label' : "20%이하", "value" : "twenty"},
                        {'label' : "30%이하", "value" : "thirty"},
                        {'label' : "30%초과", "value" : "over-thirty"}
                    ], value = 'risk-acceptance',
                    labelStyle={'display': 'inline-block', 'width': '20%', 'margin':'auto', 'marginTop': 15, 'paddingLeft': 15},
                    id = 'character-risk'
                ),
                html.Hr(style={"width" : "3000px"}),

                html.Label('4. 연간소득'),
                dcc.RadioItems(
                    options = [
                        {'label' : "3000만원 이하", "value" : "three-thousand"},
                        {'label' : "6000만원 이하", "value" : "six-thousand"},
                        {'label' : "1억 이하", "value" : "one-billion"},
                        {'label' : "2억 이하", "value" : "two-billion"},
                        {'label' : "2억 초과", "value" : "over-two-billion"}
                    ], value = 'income',
                    labelStyle={'display': 'inline-block', 'width': '20%', 'margin':'auto', 'marginTop': 15, 'paddingLeft': 15},
                    id = 'annual-income'
                ),
                html.Hr(style={"width" : "3000px"}),

                html.Label('5. 금융자산의 비중'),
                dcc.RadioItems(
                    options = [
                        {'label' : "순자산의 5%이하", "value" : "lower-five"},
                        {'label' : "10%이하", "value" : "lower-ten"},
                        {'label' : "20%이하", "value" : "lower-twenty"},
                        {'label' : "30%이하", "value" : "lower-thirty"},
                        {'label' : "30%초과", "value" : "over-thirty"}
                    ], value = 'ratio',
                    labelStyle={'display': 'inline-block', 'width': '20%', 'margin':'auto', 'marginTop': 15, 'paddingLeft': 15},
                    id = 'finance-ratio'
                ),
                html.Hr(style={"width" : "3000px"}),

                html.Label('6. 투자 기간'),
                dcc.RadioItems(
                    options = [
                        {'label' : "1년 이하", "value" : "below-one-year"},
                        {'label' : "3년 이하", "value" : "below-three-year"},
                        {'label' : "5년 이하", "value" : "below-five-year"},
                        {'label' : "5년 초과", "value" : "over-five-year"},
                    ], value = 'term',
                    labelStyle={'display': 'inline-block', 'width': '20%', 'margin':'auto', 'marginTop': 15, 'paddingLeft': 15},
                    id = 'invest-terms'
                ),
                html.Hr(style={"width" : "3000px"}),

                html.Label('7. 연령대'),
                dcc.RadioItems(
                    options = [
                        {'label' : "10대", "value" : "teenage"},
                        {'label' : "20대", "value" : "two-age"},
                        {'label' : "30대", "value" : "three-age"},
                        {'label' : "40대", "value" : "four-age"},
                        {'label' : "50대", "value" : "five-age"},
                        {'label' : "60대 이상", "value" : "six-age"}
                    ], value = 'ages',
                    labelStyle={'display': 'inline-block', 'width': '20%', 'margin':'auto', 'marginTop': 15, 'paddingLeft': 15},
                    id = 'age-check'
                ),
                html.Hr(style={"width" : "3000px"}),

                html.Label('8. 투자상품 이해에 대한 자기평가'),
                dcc.RadioItems(
                    options = [
                        {'label' : "원금손실 가능한 투자상품 경험 없음", "value" : "no-invest"},
                        {'label' : "ELS 투자경험", "value" : "ELS"},
                        {'label' : "펀드나 ETF투자경험", "value" : "fund"},
                        {'label' : "주식 투자경험", "value" : "stock"},
                    ], value = 'self-test',
                    labelStyle={'display': 'inline-block', 'width': '20%', 'margin':'auto', 'marginTop': 15, 'paddingLeft': 15},
                    id = 'self-understand-degree'
                )
            ], id = 'check-list'),

        html.Br(),
        html.Br(),
        html.Button('Submit', id='submit-val', style = {"background-color" : "Yellow"}, n_clicks=0),
        html.Div(
            id = 'character-result'
        )
        ]
        return layout