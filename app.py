from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_system.components.llm_response.generate_response import LLMResponseGenerator
import logging
app = Flask(__name__)
CORS(app)

searcher = LLMResponseGenerator()
# Cấu hình logger
# logging.basicConfig(level=logging.DEBUG)  # Thiết lập mức log
# logger = logging.getLogger(__name__)

@app.route('/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()

        # Lấy index_name, user_query, và chat_history từ data
        index_name = data.get("index_name", "dama_index")
        user_query = data.get("user_query")
        # Nếu client không gửi kèm chat_history, mặc định là []
        chat_history = data.get("chat_history", [])

        if not user_query:
            return jsonify({"error": "user_query is required"}), 400

        # Gọi hàm generate_response mới, truyền kèm chat_history
        answer = searcher.generate_response(index_name, user_query, chat_history)

        # Hàm generate_response sẽ cập nhật chat_history (append user & bot),
        # do đó chat_history đã được chỉnh sửa trong quá trình gọi. 
        # Trả về response kèm chat_history đã cập nhật để client lưu
        return jsonify({
            "response": answer,
            "chat_history": chat_history
        })

    except Exception as e:
        # logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)