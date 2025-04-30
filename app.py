from flask import Flask, request, jsonify  # <-- This import was missing
from flask_cors import CORS
from main import run_agent  # Your function to handle the query

app = Flask(__name__)  # ✅ Only create the app once
CORS(app)  # ✅ Enable CORS

@app.route('/query', methods=['POST'])
def query_agent():
    user_query = request.json.get('query')
    if user_query:
        response = run_agent(user_query)
        return jsonify({"response": response})
    return jsonify({"error": "No query provided"}), 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
