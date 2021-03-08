import dash
import dash_html_components as html
import dash_core_components as dcc
import DateTime
import Tab, SignUp, Analysis, Info
import copy
from dash.dependencies import Input, Output, State

class App:
    def __init__(self):
        self.sheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = dash.Dash(__name__, external_stylesheets=self.sheet)
        self.tab = Tab.Tab()
        self.signup = SignUp.SignUp()
        self.analysis = Analysis.Analysis()
        self.info = Info.Info()

    def show_content(self):
        app = self.app
        tab = self.tab
        signup = self.signup
        origin = tab.layout()
        app.layout = html.Div(tab.layout()+signup.layout())

        @app.callback(
            Output(self.tab.output_id, "children"),
            Input(self.tab.input_id, "value")
        )
        def show_page(tab):
            if tab == 'tab-1':
                temp = origin + signup.layout()
                app.layout = html.Div(temp)

            if tab == 'tab-2':
                app.layout = html.Div(analysis.layout())

            if tab == 'tab-3':
                app.layout = html.Div(info.layout())


        @app.callback(
            Output("character-result", 'children'),
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
        def show_page(n_clicks, input_1, input_2, input_3, input_4,
                      input_5, input_6, input_7, input_8, input_9, input_10,
                      input_11):

            if 0<n_clicks:
                print(input_1, input_2, input_3, input_4, input_5, input_6,
                      input_7, input_8, input_9, input_10, input_11)






