from flask import Flask
from app.db import db_close

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = "yoursecretkey",
    )

    # close db connection when request ends.
    app.teardown_appcontext(db_close)

    # Import routes
    from app import routes
    routes.init_app(app)

    return app