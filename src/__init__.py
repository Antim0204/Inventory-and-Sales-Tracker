# src/__init__.py
from flask import Flask
from .config import Settings
from .db import init_engine, init_session_factory
from .errors import register_error_handlers
from .apis import register_blueprints
from .logger import setup_logger

from flasgger import Swagger

def create_app() -> Flask:
    app = Flask(__name__)

    # Load settings
    settings = Settings()
    app.config["SETTINGS"] = settings
    logger = setup_logger("inventory_app")
    app.logger = logger
    # DB wiring
    engine = init_engine(settings.DATABASE_URL)
    session_factory = init_session_factory(engine)
    app.config["DB_ENGINE"] = engine
    app.config["SESSION_FACTORY"] = session_factory

    # Swagger 2.0 (NOT OpenAPI 3)
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Fuel Station Inventory & Sales API",
            "version": "1.0.0",
            "description": "Manage fuel types, inventory refills, and sales with atomic rules.",
        },
        "basePath": "/",
        "schemes": ["http"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
    }
    swagger_config = {
        "headers": [],
        "specs": [
            {"endpoint": "apispec_1", "route": "/apispec_1.json",
             "rule_filter": lambda rule: True, "model_filter": lambda tag: True}
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs",
    }
    Swagger(app, template=swagger_template, config=swagger_config)

    register_blueprints(app)
    register_error_handlers(app)
    return app
