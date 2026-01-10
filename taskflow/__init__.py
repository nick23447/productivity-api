from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from taskflow.config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import sqlalchemy as sa

db: SQLAlchemy= SQLAlchemy()
bcrypt: Bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class: type[Config] = Config) -> Flask:
    app: Flask = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    from taskflow.users.routes import users
    from taskflow.tasks.routes import tasks
    
    app.register_blueprint(users)
    app.register_blueprint(tasks)

    with app.app_context():
        db.create_all()

    return app

