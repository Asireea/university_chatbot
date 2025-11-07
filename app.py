from flask import Flask, request, jsonify, send_from_directory, render_template
from main import run_workflow
import os

app = Flask(__name__)

# GLOBAL STATE: This dictionary will store the conversation history
# Since we only have one endpoint for now, we treat it as a single chat session
conversation_history = [] 

@app.route("/")
def index():
    # Serve the index.html file from the same directory
    #return send_from_directory(os.getcwd(), "index.html")
    return render_template('index.html')

@app.route("/run", methods=["POST"])
def run():
    global conversation_history
    
    try:
        data = request.get_json(force=True)
        user_input = data.get("user_input")

        if not user_input:
             return jsonify({"error": "Missing 'user_input'."}), 400

        # 1. Add current history to the request data before calling the workflow
        data["chat_history"] = conversation_history

        print("Received data (with history):", data)
        
        # 2. Run the workflow
        result = run_workflow(data)
        
        # Check for errors from the workflow
        if "error" in result:
             return jsonify(result), 500

        print("Result:", result)
        
        # 3. Update the global history with the new history returned by the workflow
        conversation_history = result.get("chat_history", [])
        
        # 4. Return just the agent output to the client
        return jsonify({
            "agent_output": result["agent_output"]
        })
        
    except Exception as e:
        print("Error in /run route:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
