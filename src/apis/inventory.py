# src/apis/inventory.py
from flask import Blueprint, current_app, jsonify, request
from marshmallow import ValidationError as MsValidationError
from src.db import session_scope
from src.modules.inventory_service import refill_stock, list_inventory
from src.errors import ValidationError
from src.models.schemas import RefillStockIn

bp = Blueprint("inventory", __name__, url_prefix="/inventory")

@bp.post("/refill")
def refill():
    """
    Refill Inventory
    ---
    tags:
      - Inventory
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [fuel_type_id, litres]
          properties:
            fuel_type_id: { type: integer, example: 1 }
            litres: { type: string, example: "100.000" }
    responses:
      200: { description: OK }
      400: { description: Validation error }
      404: { description: Fuel type not found }
    """
    try:
        payload = RefillStockIn().load(request.get_json(force=True))
    except MsValidationError as e:
        raise ValidationError(e.messages)
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = refill_stock(s, payload["fuel_type_id"], payload["litres"])
    return jsonify(res), 200

@bp.get("")
def get_inventory():
    """
    Get Inventory
    ---
    tags:
      - Inventory
    responses:
      200:
        description: OK
        schema:
          type: array
          items:
            type: object
            properties:
              fuel_type_id: { type: integer }
              name: { type: string }
              stock_litres: { type: string }
    """
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = list_inventory(s)
    return jsonify(res), 200
