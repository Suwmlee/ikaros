
from src import create_app

application = create_app()

if __name__ == "__main__":
    application.run(host='127.0.0.1', port=12346, debug=True)
