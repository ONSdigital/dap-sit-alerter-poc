from flask.cli import load_dotenv

from app.app import setup_app

load_dotenv()


if __name__ == "__main__":
    app = setup_app()
    app.run(debug=True, host='0.0.0.0')
