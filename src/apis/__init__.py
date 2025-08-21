# src/apis/__init__.py
from flask import Flask, Blueprint, jsonify
from .fuel_types import bp as fuel_types_bp
from .inventory import bp as inventory_bp
from .sales import bp as sales_bp
from .reporting import bp as reporting_bp
def register_blueprints(app: Flask):
    # Register feature blueprints
    app.register_blueprint(fuel_types_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(reporting_bp)

    # Utility routes (root and health check)
    utility = Blueprint("utility", __name__)

    @utility.get("/")
    def index():
        """
        API Index
        ---
        tags:
          - Meta
        responses:
          200: { description: OK }
        """
        return jsonify({
            "status": "ok",
            "service": "Fuel Station Inventory & Sales API",
            "endpoints": [
                "/fuel-types",
                "/inventory",
                "/sales",
                "/health",
                "/apidocs"  # if you add Flasgger later
            ],
        }), 200

    @utility.get("/health")
    def health():
        """
        Health Check
        ---
        tags:
          - Meta
        responses:
          200: { description: OK }
        """
        return jsonify({"status": "healthy"}), 200

    app.register_blueprint(utility)
