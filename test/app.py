import copy
import psycopg2 as pg2
import dash
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State

import layout
from user import User

sheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=sheet,
                suppress_callback_exceptions=True)
server = app.server

def show_content():
    style = layout.style
    app.layout = html.Div(layout.main_login, id='main-layout')
    check = False
    user = User()

    @app.callback(
        Output('main-layout', 'children'),
        [Input('login-button', 'n_clicks'),
         Input('sign-up-button', 'n_clicks')],
        State('user-id-main', 'value')
    )
    def show_layout(login, signup, user_id):

        if user.name:
            user.id = ''
            user.name = ''

        print('#1. in show_layout, login: {}, signup: {}, user_id: {}'.format(login, signup, user_id))
        if 0 < login:
            temp = copy.deepcopy(layout.tab)
            temp.children[0].children = temp.children[0].children[1:]
            temp.children[0].value = 'analysis'
            user.name = copy.deepcopy(user_id)
            print('#3. in show_layout, login: {}, signup: {}, user.name: {}'.format(login, signup, user.name))
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
        if tab_input == 'signup':
            return html.Div(layout.signup)

        if tab_input == 'analysis':
            if not check:
                layout.analysis[0].children[1].children = ''
                layout.analysis[0].children[3].children = '8/1/2021 4:00:00 PM'
                user.date = '8/1/2021 4:00:00 PM'

            return html.Div(layout.analysis)

        if tab_input == 'info':
            if not check:
                layout.info[0].children[1].children = user.name
            return html.Div(layout.info)

    @app.callback(
        [Output('output-pos', 'children'),
         Output('max-date', 'children')],
        Input('predict-slider', 'value')
    )
    def show_prediction(select):

        print('app.py show_prediction params: user.date {}, user.userid {}, user.name {}'.format(user.date, user.userid,
                                                                                                 user.name))
        conn = pg2.connect(database="d2ke5vkurjkusr", user="kdyjpzwsyqrqpb",
                           password="6b610da9417e361c2af3be1fd0c179061b5b258f0e6f7ff9e1da464ba221e46c",
                           host="ec2-35-174-35-242.compute-1.amazonaws.com", port="5432")
        cur = conn.cursor()
        cur.execute("select distinct userid, name from userselection")
        conn.commit()
        user_list = cur.fetchall()
        user_dict = {u[1]: u[0] for u in user_list}
        user.userid = user_dict[user.name]
        print("userid : {}".format(user.userid))
        df_comp_pkl = pd.read_pickle('./data/processed/comparison_0801_{}.pkl'.format(user.userid))
        return [html.Div(), "xxxx"]

    @app.callback(
        Output('modal-detail-info', 'is_open'),
        Output('record', 'children'),
        [Input('detail-info-button', 'n_clicks'),
         Input('close-detail-info', 'n_clicks')],
        State('modal-detail-info', 'is_open'),
        State('predict-slider', 'value')
    )
    def detailInfo(open, close, is_open, select):
        return

    @app.callback(
        Output('detail-info-output', 'children'),
        [Input('default-predict-date', 'date')]
    )
    def page3OutputResult(pDate):
        try:
            temp = pDate.split('-')
            pDate = temp[1] + '/' + temp[2] + '/' + temp[0] + ' 4:00:00 PM'
        except:
            pDate += ' 4:00:00 PM'

        print('Selected date: {}'.format(pDate))
        print(user.name)
        result = user.page3Data(pDate)

        return


show_content()

if __name__ == '__main__':
    app.run_server(debug=True)
