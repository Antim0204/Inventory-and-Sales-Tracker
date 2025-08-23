# src/apis/schemas.py
from marshmallow import Schema, fields, validates, ValidationError, pre_load
from decimal import Decimal

class CreateFuelTypeIn(Schema):
    name = fields.String(required=True)
    price_per_litre = fields.Decimal(required=True, as_string=True, places=3)
    initial_stock_litres = fields.Decimal(load_default=Decimal("0.000"), as_string=True, places=3)
    
    @validates("price_per_litre")
    def _price_ge_0(self, v):
        if v is None or v < 0: raise ValidationError("price_per_litre must be >= 0")

    @validates("initial_stock_litres")
    def _stock_ge_0(self, v):
        if v is None or v < 0: raise ValidationError("initial_stock_litres must be >= 0")

class UpdatePriceIn(Schema):
    price_per_litre = fields.Decimal(required=True, as_string=True, places=3)

    @validates("price_per_litre")
    def _price_ge_0(self, v):
        if v < 0: raise ValidationError("price_per_litre must be >= 0")

class RefillStockIn(Schema):
    fuel_type_id = fields.Integer(required=True)
    litres = fields.Decimal(required=True, as_string=True, places=3)

    @validates("litres")
    def _litres_gt_0(self, v):
        if v <= 0: raise ValidationError("litres must be > 0")

class RecordSaleIn(Schema):
    fuel_type_id = fields.Integer(required=True)
    litres = fields.Decimal(required=True, as_string=True, places=3)

    @validates("litres")
    def _litres_gt_0(self, v):
        if v <= 0: raise ValidationError("litres must be > 0")

class SalesQuery(Schema):
    from_ = fields.DateTime(load_default=None, data_key="from")
    to = fields.DateTime(load_default=None, data_key="to")
    fuel_type_id = fields.Integer(load_default=None)
    @pre_load
    def parse_dates(self, data, **kwargs):
        # Convert ImmutableMultiDict to a mutable dict
        data = dict(data)
        for key in ["from", "to"]:
            if key in data and len(data[key]) == 10:  # Only YYYY-MM-DD
                if key == "from":
                    data[key] += "T00:00:00"
                else:
                    data[key] += "T23:59:59"
        return data

class ReportQuery(Schema):
    from_ = fields.DateTime(load_default=None, data_key="from")
    to = fields.DateTime(load_default=None, data_key="to")
    fuel_type_id = fields.Integer(load_default=None)
    granularity = fields.String(load_default="day")  # day|week|month
    @pre_load
    def parse_dates(self, data, **kwargs):
        # Convert ImmutableMultiDict to mutable dict
        data = dict(data)
        for key in ["from", "to"]:
            if key in data and len(data[key]) == 10:  # YYYY-MM-DD
                if key == "from":
                    data[key] += "T00:00:00"
                else:
                    data[key] += "T23:59:59"
        return data
