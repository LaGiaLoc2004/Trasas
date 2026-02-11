# Trasas
Đây là bản rút gọn, tập trung vào các bước thực hiện nhanh:

---

# 📖 Hướng dẫn chạy RAG System

### 1. Cài đặt công cụ bắt buộc

* **Tesseract OCR**: [Link tải](https://www.google.com/search?q=https://github.com/UB-Mannheim/tesseract/wiki)
* **Poppler**: [Link tải](https://github.com/oschwartz10612/poppler-windows/releases) (Giải nén lấy thư mục `bin`).

### 2. Cài đặt thư viện

```bash
pip install opencv-python pytesseract python-docx pandas pdf2image tiktoken langchain-text-splitters sentence-transformers faiss-cpu

```

### 3. Cấu hình Code

Mở file Python và cập nhật 3 đường dẫn này:

1. `TESSERACT_PATH`: Trỏ tới file `.exe` của Tesseract.
2. `POPPLER_PATH`: Trỏ tới thư mục `bin` của Poppler.
3. `file_path`: Trỏ tới file tài liệu bạn muốn dùng.

### 4. Cách hoạt động

1. **Chạy file:** `python your_file_name.py`.
2. **Xử lý:** Chương trình tự động đọc file -> Chia nhỏ (Chunking) -> Chuyển thành vector (Embedding) -> Lưu vào `rag.db`.
3. **Hỏi đáp:** Nhập câu hỏi trực tiếp vào terminal để tìm kiếm nội dung liên quan.

---

**Lưu ý:** Nếu muốn đổi tài liệu mới, hãy xóa file `rag.db` để hệ thống cập nhật lại từ đầu.
