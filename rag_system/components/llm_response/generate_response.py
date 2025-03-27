from rag_system.services.azure_openai import AzureOpenAIClient
from rag_system.components.search.azure_search import AzureSearch

import os
from dotenv import load_dotenv

load_dotenv(override=True)

class LLMResponseGenerator: 
    def __init__(self):
        self.searcher = AzureSearch()
        self.llm_client = AzureOpenAIClient().get_client()
        self.chat_completion_model = os.getenv("OPENAI_CHAT_COMPLETION_MODEL_NAME")
        
    def generate_response(self, index_name, user_query, chat_history):
        """
        Hàm generate_response mới:
        - Thay vì tạo biến chat_history nội bộ, nó nhận chat_history từ bên ngoài.
        - Thực hiện tìm kiếm, xây dựng messages dựa trên chat_history + user_query.
        - Sau khi lấy câu trả lời, cập nhật chat_history (append user + assistant).
        - Trả về answer, để phía ngoài có thể sử dụng và tiếp tục quản lý chat_history.
        """
        # Tìm kiếm các đoạn văn bản liên quan
        search_results = self.searcher.search(index_name, user_query)
        data_source = [
            doc[os.getenv("SOURCE")] + ", page " + str(doc[os.getenv("PAGE_NUMBER")]) + ": "
            + doc[os.getenv("CONTENT")].replace("\n", "").replace("\r", "")
            for doc in search_results
        ]
        content = "\n".join(data_source)

        # Xây dựng messages cho OpenAI
        # Bắt đầu với 1 system message, sau đó là toàn bộ chat_history + user_query
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant trained to answer queries based on "
                    "the following information:\n" + content
                    + "\nProvide sourcefile and the page number you used to answer the question."
                )
            }
        ] + chat_history + [
            {"role": "user", "content": user_query}
        ]

        # Gọi OpenAI Chat Completion
        response = self.llm_client.chat.completions.create(
            model=self.chat_completion_model,
            messages=messages
        )

        answer = response.choices[0].message.content

        # Cập nhật chat_history với tin nhắn của user và phản hồi của bot
        chat_history.append({"role": "user", "content": user_query})
        chat_history.append({"role": "assistant", "content": answer})

        return answer