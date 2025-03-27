from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from services.text_qa import generate_answer
from typing import Union, Dict, Any

app = Flask(__name__)
CORS(app)


@app.route('/generate_response', methods=['POST'])
def generate_response() -> Union[Response, tuple[Response, int]]:
    """
    Generate a response based on the user's query using a RAG (Retrieval-Augmented Generation) approach.

    Expected JSON payload:
    {
        "index_name": str,  # Optional. Default: "text_embeddings"
        "user_query": str   # Required. The user's question
    }

    Returns:
        Union[Response, tuple[Response, int]]: JSON response containing either:
            - Success: {"response": str} with status code 200
            - Error: {"error": str} with status code 400 or 500
    """
    try:
        data: Dict[str, Any] = request.get_json()
        index_name: str = data.get("index_name", "text_embeddings")
        user_query: str = data.get("user_query")

        if not user_query:
            return jsonify({"error": "user_query is required"}), 400

        answer: str = generate_answer(user_query, k=3, index_name=index_name)

        return jsonify({
            "response": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
