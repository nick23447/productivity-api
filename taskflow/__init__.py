from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from taskflow.config import Config
from flask_migrate import Migrate
import sqlalchemy as sa

db: SQLAlchemy= SQLAlchemy()
migrate: Migrate = Migrate()
bcrypt: Bcrypt = Bcrypt()

def create_app(config_class: type[Config] = Config) -> Flask:
    app: Flask = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    
    from taskflow.users.routes import users
    
    app.register_blueprint(users)

    engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    inspector = sa.inspect(engine)

    return app