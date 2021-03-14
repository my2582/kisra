import App

if __name__ == '__main__':
    app = App.App()
    app.show_content()
    app.app.run_server(debug = True)