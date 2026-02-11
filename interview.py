import sqlite3
import unicodedata
import cv2
import pytesseract
from docx import Document
import pandas as pd
from pdf2image import convert_from_path
import os
import uuid
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

TESSERACT_PATH = r'L:\Intern\trasas\tesseract\tesseract.exe'
POPPLER_PATH = r'L:\Intern\trasas\Release-25.12.0-0\poppler-25.12.0\Library\bin' # Thư mục bin của Poppler

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# trích dữ liệu
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    content_list = []
    try:
        # 1. png, jpg
        if ext in ['.png', '.jpg']:
            image = cv2.imread(file_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            text = clean_text(pytesseract.image_to_string(gray, lang='vie+eng'))
            content_list.append((text, ext))

        # 2. pdf 
        elif ext == '.pdf':
            pages = convert_from_path(file_path, poppler_path=POPPLER_PATH)
            for page_num, page_content in enumerate(pages):
                full_text = clean_text(pytesseract.image_to_string(page_content, lang='vie+eng'))
                content_list.append((full_text, f"Trang {page_num + 1}"))

        # 3. docx
        elif ext == '.docx':
            doc = Document(file_path)
            content_list.append((clean_text("\n".join([para.text for para in doc.paragraphs])), ext))

        # 4. xlsx
        elif ext in ['.xlsx']:
            xlsx = pd.ExcelFile(file_path)
            for sheet in xlsx.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet)
                text = clean_text(df.to_string())
                content_list.append((text, f"Sheet: {sheet}"))
            
        # 5. txt
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = clean_text(f.read())
                content_list.append((text, ext))

        else:
            return f"Định dạng {ext} chưa được hỗ trợ."

    except Exception as e:
        return f"Lỗi xử lý: {str(e)}"
    return content_list

# clean
def clean_text(text):
    t = unicodedata.normalize('NFC', text.replace('\x0c', ''))
    return re.sub(r'\n\s*\n', '\n\n', t).strip()

# chunking
def chunking_data(content_list, file_name):
    encoding = tiktoken.get_encoding("cl100k_base")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50,
        length_function=lambda x: len(encoding.encode(x))
    )
    
    chunks_final = []
    for text, loc in content_list:
        sub_chunks = splitter.split_text(text)
        for i, c in enumerate(sub_chunks):
            chunks_final.append({
                "id": str(uuid.uuid4()),
                "file": file_name,
                "text": c,
                "loc": loc,
                "idx": i
            })
    return chunks_final

# embedding
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def create_embeddings(chunks):
    texts = [c['text'] for c in chunks]
    vectors = model.encode(texts)
    
    # Gán vector vào chunk
    for i in range(len(chunks)):
        chunks[i]['vec'] = vectors[i]
    return chunks

def ask_question(query, index, all_chunks, k=3):
    query_vec = model.encode([query]).astype('float32')
    
    # Tìm kiếm Top-K
    # D: Distances - khoảng cách, I: Indices - thứ tự
    D, I = index.search(query_vec, k)
    
    print(f"\n>> Câu hỏi: {query}")
    results = []
    for idx in I[0]:
        chunk = all_chunks[idx]
        results.append(chunk)
        print(f"- Nguồn: {chunk['location']} | Nội dung: {chunk['text'][:100]}...")
        
    return results
   
# database
def db(chunks):
    connector = sqlite3.connect('rag.db')
    cur = connector.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS data (id TEXT, txt TEXT, loc TEXT, vec BLOB, meta TEXT)')
    
    for c in chunks:
        # Chuyển vector sang nhị phân
        v_bytes = c['vec'].astype('float32').tobytes()

        m_str = f"file:{c['file']}, index:{c['idx']}"
        
        cur.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?)", 
                    (c['id'], c['text'], c['loc'], v_bytes, m_str))
    connector.commit()

# RAG answer
def ask_me(query, k=3):
    db = sqlite3.connect('rag.db')
    cur = db.cursor()
    cur.execute("SELECT txt, loc, vec FROM data")
    rows = cur.fetchall()
    
    # FAISS từ dữ liệu vừa load trong DB lên
    all_vecs = np.array([np.frombuffer(r[2], dtype='float32') for r in rows])
    index = faiss.IndexFlatL2(all_vecs.shape[1])
    index.add(all_vecs)
    
    # Tìm kiếm
    q_vec = model.encode([query]).astype('float32')
    D, I = index.search(q_vec, k)
    
    print(f"\n[HỎI]: {query}")
    for i in I[0]:
        print(f" >> Thấy ở ({rows[i][1]}): {rows[i][0][:100]}...")


def main():
    # Khởi tạo database (nếu chưa có)
    file_path = "L:/Intern/trasas/folder_training/Chapter1.pdf"
    
    if not os.path.exists(file_path):
        print(f"Lỗi: Không tìm thấy file {file_path}")
        return

    # trích xuất và làm sạch
    print(f"Đang đọc file: {file_path}...")
    raw_data = extract_text(file_path)
    
    # chunking
    print("Đang chia nhỏ văn bản thành các mẩu (chunks)...")
    chunks = chunking_data(raw_data, os.path.basename(file_path))
    print(f"=> Tạo được {len(chunks)} đoạn văn bản.")

    # Embedding
    print("Đang chuyển văn bản thành vector (Embedding)...")
    chunks_with_vec = create_embeddings(chunks)

    # lưu vào db
    print("Đang lưu dữ liệu vào SQLite (rag.db)...")
    db(chunks_with_vec)

    # rag answer
    print("\nHệ thống đã sẵn sàng!")
    
    while True:
        user_query = input("\n Nhập câu hỏi của bạn (hoặc gõ 'exit' để thoát): ")
        if user_query.lower() in ['exit', 'quit', 'thoát']:
            break
        
        # Gọi hàm tìm kiếm
        try:
            ask_me(user_query, k=2)
        except Exception as e:
            print(f"Lỗi khi tìm kiếm: {e}")
            print("Kiểm tra xem database có rỗng không hoặc model đã tải xong chưa.")

if __name__ == "__main__":
    main()