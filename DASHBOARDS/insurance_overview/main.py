from app import create_dash_app

if __name__ == '__main__':
    
    app = create_dash_app()
    app.run_server(port=8050)