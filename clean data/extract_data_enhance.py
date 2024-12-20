import os
from pdf2image import convert_from_path
import pytesseract
import re
import json

# ضبط مسار Tesseract (تحديث المسار إذا كنت على ويندوز)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# دالة لتنظيف النصوص
def clean_text(text):
    # إزالة الفراغات الزائدة
    text = re.sub(r'\n+', '\n', text)
    # إزالة الحروف غير الإنجليزية
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # إزالة المسافات الزائدة
    text = text.strip()
    return text

# الدالة الرئيسية
def extract_text_to_json(pdf_path, output_json):
    # قائمة لتخزين النصوص المستخرجة لكل صفحة
    extracted_data = []

    # تحويل صفحات PDF إلى صور
    print("Converting PDF to images...")
    pages = convert_from_path(pdf_path, dpi=300)

    # استخراج النصوص من كل صفحة
    for i, page in enumerate(pages):
        print(f"Processing page {i + 1}...")

        # استخراج النصوص باستخدام Tesseract OCR
        text = pytesseract.image_to_string(page, lang='eng')
        cleaned_text = clean_text(text)

        # إضافة النصوص إلى القائمة
        extracted_data.append({
            "page": i + 1,
            "text": cleaned_text
        })

    # حفظ البيانات في ملف JSON
    print(f"Saving extracted data to {output_json}...")
    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

    print("Extraction completed!")

# تشغيل الكود
if __name__ == "__main__":
    # مسار ملف PDF
    pdf_path = "./booktry1.pdf"
    
    # ملف JSON للإخراج
    output_json = "./output/output_data.json"

    # تنفيذ العملية
    extract_text_to_json(pdf_path, output_json)
