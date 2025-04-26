from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)  # Вместо 'name' должно быть '__name__'
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from routes import *  # Импортируем маршруты

if __name__ == '__main__':  # Вместо 'name' должно быть '__name__'
    app.run(debug=True)
