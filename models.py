import ollama

model = "llama3.2:1b"


prompt = """
Đây là đoạn thông tin trích dẫn từ trang 1 của nghị định 13:
'Trong Nghị định này, các từ ngữ dưới đây được hiểu như sau:

1. Dữ liệu cá nhân là thông tin dưới dạng ký hiệu, chữ viết, chữ số, hình ảnh, âm thanh hoặc dạng tương tự trên môi trường điện tử gắn liền với một con người cụ thể hoặc giúp xác định một con người cụ thể. Dữ liệu cá nhân bao gồm dữ liệu cá nhân cơ bản và dữ liệu cá nhân nhạy cảm.

2. Thông tin giúp xác định một con người cụ thể là thông tin hình thành từ hoạt động của cá nhân mà khi kết hợp với các dữ liệu, thông tin lưu trữ khác có thể xác định một con người cụ thể.

3. Dữ liệu cá nhân cơ bản bao gồm:

a) Họ, chữ đệm và tên khai sinh, tên gọi khác (nếu có);

b) Ngày, tháng, năm sinh; ngày, tháng, năm chết hoặc mất tích;

c) Giới tính;

d) Nơi sinh, nơi đăng ký khai sinh, nơi thường trú, nơi tạm trú, nơi ở hiện tại, quê quán, địa chỉ liên hệ;

đ) Quốc tịch;

e) Hình ảnh của cá nhân;

g) Số điện thoại, số chứng minh nhân dân, số định danh cá nhân, số hộ chiếu, số giấy phép lái xe, số biển số xe, số mã số thuế cá nhân, số bảo hiểm xã hội, số thẻ bảo hiểm y tế;

h) Tình trạng hôn nhân;

i) Thông tin về mối quan hệ gia đình (cha mẹ, con cái);

k) Thông tin về tài khoản số của cá nhân; dữ liệu cá nhân phản ánh hoạt động, lịch sử hoạt động trên không gian mạng;'

cho câu hỏi: 'dữ liệu cá nhân là gì?'
Hãy đưa ra câu trả lời thân thiện hơn - và làm rõ từ tài liệu nào trang bao nhiêu
Chỉ đưa ra câu trả lời, không nói gì hơn
"""


for chunk in ollama.chat(model=model, messages=[
    {"role": "user", "content": prompt}
], stream=True):
    print(chunk["message"]["content"], end="", flush=True)  # Stream words live
