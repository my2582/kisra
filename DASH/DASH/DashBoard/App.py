import dash
import dash_html_components as html
import Character
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import layout
import User

class App:
    def __init__(self):
        self.sheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = dash.Dash(__name__, external_stylesheets=self.sheet, suppress_callback_exceptions=True)
        self.layout = layout
        self.user = User.User()

    def show_content(self):
        app = self.app
        style = self.layout.style
        tab = self.layout.tab
        origin = tab
        user = self.user
        app.layout = origin

        @app.callback(
            Output(self.layout.output_id, 'children'),
            Input(self.layout.input_id, "value"),
        )
        def show_page(tab_input):
            if tab_input == 'signup':
                app.layout.children[-1] = html.Div(self.layout.signup)
                return html.Div(self.layout.signup)

            if tab_input == 'analysis':
                app.layout.children[-1] = html.Div(self.layout.analysis)
                self.layout.analysis[0].children[1].value, self.layout.analysis[0].children[3].value = \
                    user.name, user.date
                print('analysis')
                return html.Div(self.layout.analysis)

            if tab_input == 'info':
                # app.layout = html.Div(info.layout())
                pass

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

            if 0 < n_clicks:
                tags_id = [input_1, input_2, input_3, input_4, input_5, input_6, input_7, input_8, input_9,
                           input_10, input_11]
                character = Character.Character(tags_id)
                output = app.layout.children[-1].children[-1]
                if character.empty_check():
                    answer, df = character.predict()
                    result = '당신은 {0}형 투자자입니다. 당신에게 맞는 포트폴리오를 확인해 보세요'.format(answer)
                    pie = px.pie(df, names=df.columns[-1], values=df.columns[0])
                    output.children[0].children = result
                    if len(output.children) < 3:
                        fig = dcc.Graph(id='pie-chart')
                        fig.figure = pie
                        fig.figure.layout.paper_bgcolor = style['pie_chart_style']['backgroundColor']
                        output.children.append(fig)
                    output.style = style['pie_chart_style']
                    return output

                warning = '비어있는 항목이 있습니다! 전부 체크해 주세요'
                if 2 < len(output.children):
                    output.children = output.children[:-1]
                output.children[0].children = warning
                output.style = style['pie_chart_style']
                return output



        def page2_result(content):
            if type(content) == str:
                return dcc.ConfirmDialog(
                        id='confirm',
                        message=content
                    )

            before, after = content
            table_header = [
                html.Thead(html.Tr([html.Th("시점"), html.Th("현금성"), html.Th("주식"), html.Th("채권"), html.Th("대체"), html.Th('상세정보')]))
            ]

            row1 = html.Tr([html.Td("현재"), html.Td(before[before['asset_class'] == '현금성']['value'].iloc[0]),
                            html.Td(before[before['asset_class'] == '주식']['value'].iloc[0]),
                            html.Td(before[before['asset_class'] == '채권']['value'].iloc[0]),
                            html.Td(before[before['asset_class'] == '대체']['value'].iloc[0]),
                            html.Td(html.Div([html.Button('상세정보', id='detail-info-button'),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader("상세정보"),
                                            dbc.ModalBody("A small modal.", id='record'),
                                            dbc.ModalFooter(
                                                dbc.Button("Close", id="close-detail-info", className="ml-auto")
                                            ),
                                        ],
                                        id="modal-detail-info",
                                        size="sm"
                                    )]))])

            row2 = html.Tr([html.Td("미래"), html.Td(before[before['asset_class'] == '현금성']['value'].iloc[0]),
                            html.Td(before[before['asset_class'] == '주식']['value'].iloc[0]),
                            html.Td(before[before['asset_class'] == '채권']['value'].iloc[0]),
                            html.Td(before[before['asset_class'] == '대체']['value'].iloc[0]),
                            html.Td('')],
                            style={'background-color': '#FFA500'})


            # if not content[-1]:
            #     row2.style['background-color'] = '#ddd'
            #     return html.Div(dbc.Table(table_header, html.Tbody([row1, row2]), bordered=True))

            return html.Div(dbc.Table(table_header + [html.Tbody([row1, row2])], bordered=True))

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

        @app.callback(
            Output('output-pos', 'children'),
            Input('predict-slider', 'value'),
            State('analysis-name', 'value'),
            State('analysis-datetime', 'value')
        )
        def show_prediction(select, name, date):
            user.name, user.date = name, date
            select = changePeriod(select)
            result = user.closeData(select)
            return page2_result(result)

        @app.callback(
            Output('modal-detail-info', 'is_open'),
            Output('record', 'children'),
            [Input('detail-info-button', 'n_clicks'),
             Input('close-detail-info', 'n_clicks')],
            State('modal-detail-info', 'is_open'),
            State('predict-slider', 'value')
        )
        def detailInfo(open, close, is_open, select):
            select = changePeriod(select)
            result = user.closeData(select, True)
            table_header = [
                html.Thead(html.Tr([html.Th(col) for col in list(result.columns)]))
            ]

            rows = result.values.tolist()
            table_row = list()
            for row in rows:
                temp = [html.Td(data) for data in row]
                table_row.extend([html.Tr(temp)])

            result = html.Div(dbc.Table(table_header + [html.Tbody(table_row)], bordered=True))
            if open or close:
                return not is_open, result
            return is_open, result
