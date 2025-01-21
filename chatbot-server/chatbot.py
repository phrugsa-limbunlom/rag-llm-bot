from flask import Flask, request, jsonify
from flask_cors import CORS

from service.chatbot_service import ChatbotService

app = Flask(__name__)

# set CORS allow for all routes
CORS(app)


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("query")

    if not user_input:
        return jsonify({"error": "Query not provided"}), 400

    try:
        response = service.generate_answer(query=user_input)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    service = ChatbotService()
    service.initialize_service()
    # run flask app
    app.run(host="0.0.0.0", port=5000)
