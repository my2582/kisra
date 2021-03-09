import dash
import dash_html_components as html
import Tab
import SignUp
import Character
import Analysis
import Info
from dash.dependencies import Input, Output, State
import json
import os
import Character
import plotly.express as px
import dash_core_components as dcc
import MapCall

class App:
    def __init__(self):
        with open(os.getcwd()+'/Styles.json', 'rb') as f:
            self.style = json.load(f)
        self.sheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = dash.Dash(__name__, external_stylesheets=self.sheet)

    def show_content(self):
        style = self.style
        app = self.app
        tab = Tab.Tab(style)
        signup = SignUp.SignUp(tab.output_id)
        anal = Analysis.Analysis(tab.output_id)
        # info = Info.Info(user)
        origin = tab.layout()
        app.layout = html.Div(origin)
        app.layout.children[-1] = html.Div(signup.layout(), id=app.layout.children[-1].id)

        @app.callback(
            State(tab.output_id, "children"),
            Input(tab.input_id, "value")
        )
        def show_page(tab):
            id = app.layout.children[-1].id
            if tab == 'tab-1':
                app.layout.children[-1] = html.Div(signup.layout(), id=app.layout.children[-1].id)
                return signup.layout()
            if tab == 'tab-2':
                app.layout.children[-1] = html.Div(anal.layout(), id=id)
                return anal.layout()

            if tab == 'tab-3':
                # app.layout = html.Div(info.layout())
                pass

        # @app.callback(
        #     Output('output-div', 'children'),
        #     Input('submit-val', 'n_clicks'),
        #     State('self-understand-degree', 'value'),
        #     State('age-check', 'value'),
        #     State('invest-terms', 'value'),
        #     State('finance-ratio', 'value'),
        #     State('annual-income', 'value'),
        #     State('character-risk', 'value'),
        #     State('invest-purpose', 'value'),
        #     State('invest-experience', 'value'),
        #     State('invest-scale', 'value'),
        #     State('datetime', 'value'),
        #     State('name', 'value')
        # )
        # def show_page(n_clicks, input_1, input_2, input_3, input_4,
        #               input_5, input_6, input_7, input_8, input_9, input_10,
        #               input_11):
        #     if 0 < n_clicks:
        #         tags_id = [input_1, input_2, input_3, input_4, input_5, input_6, input_7, input_8, input_9,
        #                    input_10, input_11]
        #         character = Character.Character(tags_id)
        #         output = app.layout.children[-1].children[-1]
        #         if character.empty_check():
        #             answer, df = character.predict()
        #             result = '당신은 {0}형 투자자입니다. 당신에게 맞는 포트폴리오를 확인해 보세요'.format(answer)
        #             pie = px.pie(df, names=df.columns[-1], values=df.columns[0])
        #             output.children[0].children = result
        #             if len(output.children) < 3:
        #                 fig = dcc.Graph(id='pie-chart')
        #                 fig.figure = pie
        #                 fig.figure.layout.paper_bgcolor = style['pie_chart_style']['backgroundColor']
        #                 output.children.append(fig)
        #             output.style = style['pie_chart_style']
        #             return output
        #
        #         warning = '비어있는 항목이 있습니다! 전부 체크해 주세요'
        #         if 2 < len(output.children):
        #             output.children = output.children[:-1]
        #         output.children[0].children = warning
        #         output.style = style['pie_chart_style']
        #         return output