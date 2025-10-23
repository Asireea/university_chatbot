from flask import Flask, request, jsonify, send_from_directory, render_template
from main import run_workflow
import os

app = Flask(__name__)

@app.route("/")
def index():
    # Serve the index.html file from the same directory
    #return send_from_directory(os.getcwd(), "index.html")
    return render_template('index.html')

@app.route("/run", methods=["POST"])
def run():
    try:
        data = request.get_json(force=True)
        print("Received data:", data)
        result = run_workflow(data)
        print("Result:", result)
        return jsonify(result)
    except Exception as e:
        print("Error in /run route:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
