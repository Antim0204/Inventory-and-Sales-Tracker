# src/apis/fuel_types.py
from flask import Blueprint, current_app, jsonify, request
from marshmallow import ValidationError as MsValidationError
from src.db import session_scope
from src.modules.fuel_types_service import create_fuel_type, update_price, list_fuel_types
from src.errors import ValidationError
from src.models.schemas import CreateFuelTypeIn, UpdatePriceIn

bp = Blueprint("fuel_types", __name__, url_prefix="/fuel-types")

@bp.post("")
def create():
    """
    Create Fuel Type
    ---
    tags:
      - Fuel Types
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [name, price_per_litre]
          properties:
            name: { type: string, example: Diesel }
            price_per_litre: { type: string, example: "90.000" }
            initial_stock_litres: { type: string, example: "500.000" }
    responses:
      201:
        description: Created
        schema:
          type: object
          properties:
            id: { type: integer }
            name: { type: string }
            price_per_litre: { type: string }
            stock_litres: { type: string }
            created_at: { type: string }
      400:
        description: Validation error
    """
    try:
        payload = CreateFuelTypeIn().load(request.get_json(force=True))
    except MsValidationError as e:
        raise ValidationError(e.messages)
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = create_fuel_type(s, payload["name"], payload["price_per_litre"], payload["initial_stock_litres"])
    return jsonify(res), 201

@bp.patch("/<int:fuel_type_id>/price")
def patch_price(fuel_type_id: int):
    """
    Update Fuel Price
    ---
    tags:
      - Fuel Types
    parameters:
      - in: path
        name: fuel_type_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [price_per_litre]
          properties:
            price_per_litre: { type: string, example: "92.500" }
    responses:
      200: { description: Updated }
      400: { description: Validation error }
      404: { description: Fuel type not found }
    """
    try:
        payload = UpdatePriceIn().load(request.get_json(force=True))
    except MsValidationError as e:
        raise ValidationError(e.messages)
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = update_price(s, fuel_type_id, payload["price_per_litre"])
    return jsonify(res), 200

@bp.get("")
def list_():
    """
    List Fuel Types
    ---
    tags:
      - Fuel Types
    responses:
      200:
        description: OK
        schema:
          type: array
          items:
            type: object
            properties:
              id: { type: integer }
              name: { type: string }
              price_per_litre: { type: string }
    """
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = list_fuel_types(s)
    return jsonify(res), 200
