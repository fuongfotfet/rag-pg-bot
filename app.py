from flask import Flask, request, jsonify
from flask_cors import CORS
from module2 import generate_answer  # import hàm generate_answer mới

app = Flask(__name__)
CORS(app)

@app.route('/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        # Lấy index_name và user_query từ data; nếu không gửi index_name, mặc định là 'text_embeddings'
        index_name = data.get("index_name", "text_embeddings")
        user_query = data.get("user_query")

        if not user_query:
            return jsonify({"error": "user_query is required"}), 400

        # Gọi hàm generate_answer với các tham số cần thiết
        answer = generate_answer(user_query, k=3, index_name=index_name)

        # Trả về kết quả dưới dạng JSON
        return jsonify({
            "response": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)