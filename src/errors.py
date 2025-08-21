# src/errors.py
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

# Domain-specific errors
class NotFoundError(Exception):
    """Raised when a domain resource is not found."""


class ValidationError(Exception):
    """Raised when input validation fails."""


class InsufficientStockError(Exception):
    """Raised when a sale would exceed available stock."""


class ConflictError(Exception):
    """Raised when a unique constraint or duplicate resource conflict occurs."""


def register_error_handlers(app: Flask):
    # ---- Domain errors ------------------------------------------------------
    @app.errorhandler(NotFoundError)
    def _not_found(e):
        return jsonify(error={"code": "NOT_FOUND", "message": str(e)}), 404

    @app.errorhandler(ValidationError)
    def _bad_request(e):
        return jsonify(error={"code": "BAD_REQUEST", "message": str(e)}), 400

    @app.errorhandler(InsufficientStockError)
    def _insufficient(e):
        return jsonify(error={"code": "INSUFFICIENT_STOCK", "message": str(e)}), 409

    @app.errorhandler(ConflictError)
    def _conflict(e):
        return jsonify(error={"code": "CONFLICT", "message": str(e)}), 409

    # ---- Built-in Flask/Werkzeug HTTP errors (e.g., 404 on wrong URL) ------
    @app.errorhandler(HTTPException)
    def _http_exception(e: HTTPException):
        return (
            jsonify(
                error={
                    "code": e.name.replace(" ", "_").upper(),
                    "message": e.description,
                }
            ),
            e.code,
        )

    # ---- Unexpected errors (last resort) -----------------------------------
    @app.errorhandler(Exception)
    def _unhandled(e):
        # Log full stack for operators; keep client message generic
        try:
            app.logger.exception(
                "Unhandled error",
                extra={"path": request.path, "method": request.method},
            )
        except Exception:
            # Logging itself should never crash the handler
            pass

        return (
            jsonify(
                error={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
        )
