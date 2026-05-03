import os
import argparse
import json
import requests
import fitz  # PyMuPDF
from docx import Document

# 預設使用的 Ollama API 網址 (根據您的 n8n 環境配置)
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "nomic-embed-text"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def get_embedding(text):
    """呼叫本地 Ollama 生成向量"""
    try:
        response = requests.post(OLLAMA_EMBED_URL, json={
            "model": MODEL_NAME,
            "prompt": text
        }, timeout=600)
        response.raise_for_status()
        return response.json().get("embedding", [])
    except requests.exceptions.Timeout:
        print(f"⌛ 請求超時，嘗試再次連線...")
        # 再次嘗試一次
        try:
             response = requests.post(OLLAMA_EMBED_URL, json={
                "model": MODEL_NAME,
                "prompt": text
            }, timeout=300)
             return response.json().get("embedding", [])
        except:
             return []
    except Exception as e:
        print(f"❌ 向量生成失敗: {e}")
        return []

def chunk_text(text, chunk_size, overlap):
    """簡單的字數切片，帶有重疊區段"""
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start += chunk_size - overlap
    return chunks

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text() + "\n"
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def process_file(file_path):
    if not os.path.isfile(file_path):
        print(f"⚠️ 找不到檔案: {file_path}")
        return

    base_name, ext = os.path.splitext(file_path)
    ext = ext.lower()
    doc_name = os.path.basename(file_path)
    output_path = f"{base_name}_knowledge.json"

    print(f"📄 正在解析: {doc_name}")
    try:
        if ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        elif ext == ".docx":
            text = extract_text_from_docx(file_path)
        elif ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            print(f"⚠️ 略過不支援的格式: {file_path}")
            return

        print(f"✂️ 正在進行文本切割 (Chunk Size: {CHUNK_SIZE})...")
        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        
        results = []
        for i, chunk in enumerate(chunks):
            print(f"🧬 正在生成向量 ({i+1}/{len(chunks)})...", end="\r")
            embedding = get_embedding(chunk)
            if embedding:
                results.append({
                    "document_name": doc_name,
                    "content": chunk,
                    "embedding": embedding
                })
        print("\n✅ 向量生成完成！")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"🎉 檔案已匯出準備上傳至 N8N: {os.path.basename(output_path)}")

    except Exception as e:
        print(f"❌ 處理檔案失敗: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="離線知識庫文件處理工具 (PDF/DOCX -> 帶有 Embedding 的 JSON)")
    parser.add_argument("path", help="要轉換的檔案路徑")
    
    args = parser.parse_args()
    process_file(args.path)
