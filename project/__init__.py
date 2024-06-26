from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from pathlib import Path
# New modules added for task 7 - Harris Barker
from flask_bcrypt import Bcrypt
from flask_session import Session

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-do-not-reveal'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/photos.db' # Updated for task 7 - Harris Barker
    CWD = Path(os.path.dirname(__file__))
    app.config['UPLOAD_DIR'] = CWD / "uploads"
    app.config['SESSION_TYPE'] = 'filesystem'

    db.init_app(app)
    bcrypt.init_app(app) # Added for task 7
    Session(app)

    with app.app_context():
        db.create_all()

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for auth routes in our app, added for task 7 - Harris Barker
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
