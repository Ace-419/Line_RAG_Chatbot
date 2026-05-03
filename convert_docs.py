import os
import argparse
import fitz  # PyMuPDF
from docx import Document

def convert_pdf_to_txt(pdf_path, txt_path):
    print(f"📄 正在解析 PDF: {os.path.basename(pdf_path)}")
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text() + "\n"
        
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text.strip())
        print(f"✅ 成功轉換為: {os.path.basename(txt_path)}")
    except Exception as e:
        print(f"❌ PDF 解析失敗: {e}")

def convert_docx_to_txt(docx_path, txt_path):
    print(f"📄 正在解析 DOCX: {os.path.basename(docx_path)}")
    try:
        doc = Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text.strip())
        print(f"✅ 成功轉換為: {os.path.basename(txt_path)}")
    except Exception as e:
        print(f"❌ DOCX 解析失敗: {e}")

def process_file(file_path):
    if not os.path.isfile(file_path):
        print(f"⚠️ 找不到檔案: {file_path}")
        return

    base_name, ext = os.path.splitext(file_path)
    ext = ext.lower()
    txt_path = f"{base_name}.txt"

    if ext == ".pdf":
        convert_pdf_to_txt(file_path, txt_path)
    elif ext == ".docx":
        convert_docx_to_txt(file_path, txt_path)
    else:
        print(f"⚠️ 略過不支援的格式: {file_path} (僅支援 .pdf, .docx)")

def process_directory(dir_path):
    for root, _, files in os.walk(dir_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in [".pdf", ".docx"]:
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文件解析轉換工具 (PDF/DOCX -> TXT)")
    parser.add_argument("path", help="要轉換的檔案或資料夾路徑")
    
    args = parser.parse_args()
    target_path = args.path

    if os.path.exists(target_path):
        if os.path.isdir(target_path):
            print(f"📂 開始掃描資料夾: {target_path}")
            process_directory(target_path)
        else:
            process_file(target_path)
    else:
        print(f"❌ 無效的路徑: {target_path}")
