from pdf2image import convert_from_path

# Path to Poppler binaries
poppler_path = r'C:/poppler/poppler-24.08.0/Library\bin'

# Your PDF file and output folder
pdf_path = './booktry1.pdf'
output_folder = './output'

# Convert PDF pages to images with specified Poppler path
images = convert_from_path(pdf_path, dpi=300, output_folder=output_folder, fmt='png', poppler_path=poppler_path)
