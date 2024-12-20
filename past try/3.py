import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re
import pdfplumber
import json
import csv

# تحديد مسار Tesseract إذا كان ضروريًا في حالة استخدام Windows (تأكد من تثبيت Tesseract)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# الخطوة 1: تحويل الـ PDF إلى صور
def convert_pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path,poppler_path=r"C:\poppler\poppler-24.08.0\Library\bin")
    return images

# الخطوة 2: استخراج النصوص باستخدام Tesseract
def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text

# الخطوة 3: تنظيف النصوص المستخرجة
def clean_text(text):
    cleaned_text = re.sub(r'[^A-Za-z0-9\s]+', '', text)
    return cleaned_text

# الخطوة 4: استخراج الجداول من الـ PDF باستخدام إعدادات خاصة لتحسين دقة الاستخراج
def extract_tables_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        tables = []
        for page in pdf.pages:
            table = page.extract_table(
                table_settings={
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "snap_tolerance": 3,
                }
            )
            if table:
                tables.append(table)
        return tables

# تحسين معالجة الجداول للتعامل مع خلايا فارغة أو قيم ضبابية
def process_table_data(tables):
    cleaned_tables = []
    for table in tables:
        cleaned_table = []
        for row in table:
            cleaned_row = [cell.strip() if cell else "" for cell in row]
            cleaned_table.append(cleaned_row)
        cleaned_tables.append(cleaned_table)
    return cleaned_tables

# تخزين الجداول في ملف CSV
def save_tables_to_csv(tables, output_path):
    with open(output_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        for table in tables:
            writer.writerows(table)
        print(f"Tables saved to {output_path}")

# تخزين الجداول في ملف JSON
def save_tables_to_json(tables, output_path):
    with open(output_path, 'w') as f:
        json.dump(tables, f, indent=4)
    print(f"Tables saved to {output_path}")

# الخطوة 5: تخزين النصوص في ملف JSON
def save_text_to_json(text, output_path):
    data = {"pdf_text": text}
    with open(output_path, 'w') as f:
        json.dump(data, f)
    print(f"Text saved to {output_path}")

# الخطوة 6: تشغيل الكود على ملف PDF
def process_pdf(pdf_path, output_json_path, output_csv_path):
    images = convert_pdf_to_images(pdf_path)
    extracted_text = ""
    for image in images:
        text = extract_text_from_image(image)
        extracted_text += text + "\n\n"

    cleaned_text = clean_text(extracted_text)

    tables = extract_tables_from_pdf(pdf_path)
    cleaned_tables = process_table_data(tables)

    save_text_to_json(cleaned_text, output_json_path)
    save_tables_to_csv(cleaned_tables, output_csv_path)

# مثال لاستخدام الكود:
pdf_path = './booktry1.pdf'  # استبدل بمسار ملف الـ PDF الخاص بك
output_json_path = './output/extracted_text.json'  # استبدل بمسار الملف الذي ترغب في تخزين النصوص فيه
output_csv_path = './output/extracted_tables.csv'  # استبدل بمسار الملف الذي ترغب في تخزين الجداول فيه

# تشغيل عملية استخراج النصوص والجداول
process_pdf(pdf_path, output_json_path, output_csv_path)
