from flask import Blueprint, current_app, jsonify, request
from marshmallow import ValidationError as MsValidationError
from src.db import session_scope
from .schemas import ReportQuery
from src.modules.reporting_service import (
    sales_overview, sales_timeseries, sales_by_fuel_type, price_history
)
from src.errors import ValidationError

bp = Blueprint("reporting", __name__, url_prefix="/reports")

@bp.get("/sales/overview")
def get_sales_overview():
    """
    Sales Overview KPIs
    ---
    tags:
      - Reporting
    parameters:
      - in: query
        name: from
        type: string
        format: date-time
      - in: query
        name: to
        type: string
        format: date-time
      - in: query
        name: fuel_type_id
        type: integer
    responses:
      200:
        description: OK
    """
    try:
        params = ReportQuery().load(request.args)
    except MsValidationError as e:
        raise ValidationError(e.messages)
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = sales_overview(s, params.get("from_"), params.get("to"), params.get("fuel_type_id"))
    return jsonify(res), 200

@bp.get("/sales/timeseries")
def get_sales_timeseries():
    """
    Sales Time Series
    ---
    tags:
      - Reporting
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
      - in: query
        name: granularity
        type: string
        enum: [day, week, month]
        required: false
    responses:
      200:
        description: OK
    """

    try:
        params = ReportQuery().load(request.args)
    except MsValidationError as e:
        raise ValidationError(e.messages)
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = sales_timeseries(s, params.get("from_"), params.get("to"),
                               params.get("fuel_type_id"), params.get("granularity"))
    return jsonify(res), 200

@bp.get("/sales/by-fuel-type")
def get_sales_by_fuel_type():
    """
    Sales by Fuel Type
    ---
    tags:
      - Reporting
    parameters:
      - in: query
        name: from
        type: string
        format: date-time
      - in: query
        name: to
        type: string
        format: date-time
    responses:
      200:
        description: OK
    """
    try:
        params = ReportQuery().load(request.args)
    except MsValidationError as e:
        raise ValidationError(e.messages)
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = sales_by_fuel_type(s, params.get("from_"), params.get("to"))
    return jsonify(res), 200

@bp.get("/price/history")
def get_price_history():
    """
    Price History (per fuel type)
    ---
    tags:
      - Reporting
    parameters:
      - in: query
        name: fuel_type_id
        type: integer
        required: true
      - in: query
        name: from
        type: string
        format: date-time
      - in: query
        name: to
        type: string
        format: date-time
    responses:
      200:
        description: OK
      400:
        description: Missing or invalid parameters
    """
    try:
        params = ReportQuery().load(request.args)
    except MsValidationError as e:
        raise ValidationError(e.messages)
    if not params.get("fuel_type_id"):
        raise ValidationError("fuel_type_id is required")
    sf = current_app.config["SESSION_FACTORY"]
    with session_scope(sf) as s:
        res = price_history(s, params["fuel_type_id"], params.get("from_"), params.get("to"))
    return jsonify(res), 200
