from flask import Flask, request, jsonify, send_from_directory
from main import run_workflow
import os

app = Flask(__name__)

@app.route("/")
def index():
    # Serve the index.html file from the same directory
    return send_from_directory(os.getcwd(), "index.html")

@app.route("/run", methods=["POST"])
def run():
    data = request.get_json()
    result = run_workflow(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
