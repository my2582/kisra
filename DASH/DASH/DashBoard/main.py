import Tab as tb
import dash
import App
from dash.dependencies import Input, Output

if __name__ == '__main__':
    app = App.App()
    app.show_content()
    app.app.run_server(debug = True)