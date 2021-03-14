from app import App

if __name__ == '__main__':
    app = App()
    server = app.server
    app.show_content()
    app.app.run_server(debug = True)