# main.py
import os
from src import create_app
from flask import request

app = create_app()

@app.before_request
def log_request_info():
    app.logger.info(f"➡️ {request.method} {request.path} params={request.args} body={request.get_data(as_text=True)}")

@app.after_request
def log_response_info(response):
    app.logger.info(f"⬅️ {request.method} {request.path} status={response.status}")
    return response

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))  # use 5050 by default
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)