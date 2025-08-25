# src/apis/sales.py
from flask import Blueprint, current_app, jsonify, request
from marshmallow import ValidationError as MsValidationError
from src.db import session_scope
from src.modules.sales_service import record_sale, list_sales
from src.errors import ValidationError
from src.models.schemas import RecordSaleIn, SalesQuery

bp = Blueprint("sales", __name__, url_prefix="/sales")

@bp.post("")
def create_sale():
    """
    Record Sale
    ---
    tags:
      - Sales
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [fuel_type_id, litres]
          properties:
            fuel_type_id: { type: integer, example: 1 }
            litres: { type: string, example: "50.000" }
    responses:
      201: { description: Created }
      400: { description: Validation error }
      404: { description: Fuel type not found }
      409: { description: Insufficient stock }
    """
    try:
        payload = RecordSaleIn().load(request.get_json(force=True))
    except MsValidationError as e:
        raise ValidationError(e.messages)
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = record_sale(s, payload["fuel_type_id"], payload["litres"])
    return jsonify(res), 201

@bp.get("")
def list_():
    """
    List Sales
    ---
    tags:
      - Sales
    parameters:
      - in: query
        name: from
        type: string
        format: date-time
        required: false
      - in: query
        name: to
        type: string
        format: date-time
        required: false
      - in: query
        name: fuel_type_id
        type: integer
        required: false
    responses:
      200:
        description: OK
        schema:
          type: array
          items:
            type: object
            properties:
              id: { type: integer }
              fuel_type_id: { type: integer }
              litres: { type: string }
              price_at_sale: { type: string }
              amount: { type: string }
              sold_at: { type: string }
    """
    try:
        params = SalesQuery().load(request.args)
    except MsValidationError as e:
        raise ValidationError(e.messages)
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = list_sales(s, params.get("from_"), params.get("to"), params.get("fuel_type_id"))
    return jsonify(res), 200
