import dash_html_components as html
import dash_core_components as dcc

class Analysis:
    def __init__(self, id):
        self.id = id
        pass

    def layout(self):
        layout = [
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
        ]

        return layout


