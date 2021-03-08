import dash_html_components as html
import dash_core_components as dcc
from datetime import date
import json

class Tab:

    def __init__(self):
        with open('C:\\Users\\Administrator\\IdeaProjects\\DASH\\.idea\\DashBoard\\Styles.json', 'rb') as f:
            self.style = json.load(f)
        self.bluescript = list()
        self.input_id = "tabs-styled-with-inline"
        self.output_id = 'tabs-content-inline'

    def layout(self):
        tab_style = self.style["tab_style"]
        tab_selected_style = self.style["tab_selected_style"]
        tabs_styles = self.style["tabs_styles"]

        self.bluescript = [
            dcc.Tabs(id=self.input_id, value='tab-1', children=[
                dcc.Tab(label='가입', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='RA자문', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='투자내역', value='tab-3', style=tab_style, selected_style=tab_selected_style)
            ], style=tabs_styles),
            html.Div(id=self.output_id)
        ]

        return self.bluescript


