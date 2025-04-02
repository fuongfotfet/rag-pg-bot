import ollama
import numpy as np
from sentence_transformers import CrossEncoder
from rag_system.components.search.elastic_search import ElasticSearch

class LLMResponseGenerator: 
    def __init__(self):
        self.searcher = ElasticSearch()

    def sliding_window_search(self, chunk, question, window_size=1, threshold=1):
        reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        """
        Tách đoạn văn (chunk) thành các cửa sổ với số câu window_size,
        sau đó đánh giá relevance của mỗi cửa sổ với câu hỏi bằng cross-encoder.

        Parameters:
          - chunk: đoạn văn bản (string)
          - question: câu hỏi (string)
          - window_size: số câu trong mỗi cửa sổ (mặc định 3)
          - threshold: ngưỡng để chấp nhận cửa sổ (mặc định 0.5)

        Returns:
          - best_window: cửa sổ có điểm cao nhất (string) hoặc thông báo nếu không đủ relevance
          - best_score: điểm của cửa sổ đó
        """
        # Tách chunk thành các câu. Lưu ý: điều chỉnh ký tự phân tách nếu cần.
        sentences = chunk.split('. ')
        if len(sentences) < window_size:
            windows = [" ".join(sentences)]
        else:
            windows = [" ".join(sentences[i:i+window_size]) for i in range(len(sentences) - window_size + 1)]

        # Tạo cặp (question, window) cho cross-encoder
        pairs = [(question, window) for window in windows]
        scores = reranker.predict(pairs)

        scores = np.array(scores)
        valid_windows = []
        for i in range(len(scores)):
            if scores[i] >= threshold:
                valid_windows.append({
                    "window": windows[i],
                    "score": scores[i]
                })

        # Nếu có các cửa sổ hợp lệ, trả về danh sách các cửa sổ và điểm số, ngược lại trả về thông báo không tìm thấy thông tin phù hợp
        if valid_windows:
            return valid_windows
        else:
            return "Không tìm thấy thông tin phù hợp."

    def generate_response(self, index_name, user_query, chat_history):
        search_results = self.searcher.search(index_name, user_query)
        all_best_windows = []
        
        response_markdown = "### Các văn bản liên quan\n\n"
        
        for i, hit in enumerate(search_results, start=1):
            text = hit.get('text', '') 
            source = hit.get('source', '')  
            page_number = hit.get('page_number', '') 
            score = hit.get('score', 0)  
            if score < 1.5:
                continue
            
            valid_windows = self.sliding_window_search(text, user_query, window_size=1, threshold=0.5)
            
            if valid_windows != "Không tìm thấy thông tin phù hợp.":
                combined_text = ""  # Khởi tạo một chuỗi trống để lưu trữ kết quả gộp
                for window_info in valid_windows:
                    combined_text += window_info["window"] + ". "  # Gộp các cửa sổ lại với nhau
                
            # Thêm kết quả vào response_markdown
            response_markdown += f"**Văn bản {i}:**\n"
            response_markdown += f"```\n{combined_text}\n```\n"  # Hiển thị phần văn bản đã gộp
            response_markdown += f"**Nguồn**: {source}\n"
            response_markdown += f"**Trang số**: {page_number}\n"
            response_markdown += "\n" + "-"*60 + "\n\n" 

        chat_history.append({"role": "user", "content": user_query})
        chat_history.append({"role": "assistant", "content": response_markdown})

        return response_markdown