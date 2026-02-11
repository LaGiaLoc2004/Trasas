
# 🤖 AI Recruitment Assistant (RAG with Gemini)

Dự án này là một hệ thống **Retrieval-Augmented Generation (RAG)** cho phép người dùng đặt câu hỏi dựa trên nội dung của các tài liệu (PDF, Docx, Excel, Ảnh). Hệ thống sử dụng mô hình **Gemini 1.5 Flash** để sinh câu trả lời dựa trên ngữ cảnh được tìm thấy.

## ✨ Tính năng chính

* **Đa dạng nguồn dữ liệu**: Hỗ trợ đọc file PDF (OCR), Hình ảnh, Word (.docx), Excel (.xlsx) và Text (.txt).
* **OCR Tiếng Việt**: Sử dụng Tesseract để nhận diện chữ viết tay hoặc chữ trong ảnh/PDF cực kỳ chính xác.
* **Tìm kiếm ngữ nghĩa**: Sử dụng thư viện FAISS và Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`) để hiểu ý nghĩa câu hỏi thay vì chỉ khớp từ khóa.
* **Sinh câu trả lời thông minh**: Kết hợp với Google Gemini AI để đưa ra câu trả lời tự nhiên, có trích dẫn nguồn cụ thể.

## 🛠️ Yêu cầu hệ thống

1. **Python 3.10+**
2. **Tesseract OCR**: Cài đặt vào máy và trỏ đường dẫn trong code.
3. **Poppler**: Cài đặt để hỗ trợ chuyển đổi PDF sang ảnh.

## 🚀 Hướng dẫn cài đặt

1. **Cài đặt các thư viện cần thiết:**
```bash
pip install opencv-python pytesseract python-docx pandas pdf2image tiktoken langchain-text-splitters sentence-transformers faiss-cpu google-generativeai python-dotenv

```


2. **Cấu hình API Key:**
Tạo file `.env` tại thư mục gốc và dán API Key của bạn vào:
```env
GEMINI_API_KEY=your_api_key_here

```


3. **Cấu hình đường dẫn công cụ (interview.py):**
Đảm bảo các biến `TESSERACT_PATH` và `POPPLER_PATH` trỏ đúng vào thư mục cài đặt trên máy của bạn.

## 📖 Cách sử dụng

1. Đưa tài liệu bạn muốn huấn luyện vào thư mục `folder_training`.
2. Chạy chương trình: `python interview.py`.
3. Hệ thống sẽ tiến hành đọc, chia nhỏ (chunking), tạo vector và lưu vào `rag.db`.
4. Nhập câu hỏi tại Terminal để trò chuyện với tài liệu của bạn.
