import re
import json

def split_into_sentences(text):
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    sentences = sentence_endings.split(text)
    return sentences

def split_into_paragraphs(text):
    paragraphs = text.split("\n\n")
    if len(paragraphs) == 1:
        paragraphs = text.split(". ")
    return paragraphs

def split_long_headings(heading):
    # Split long headings into multiple smaller sections if they exceed a certain length
    max_length = 80  # Arbitrary limit for heading length
    words = heading.split()
    new_headings = []
    current_heading = ""
    
    for word in words:
        if len(current_heading + " " + word) > max_length:
            new_headings.append(current_heading.strip())
            current_heading = word
        else:
            current_heading += " " + word
    if current_heading:
        new_headings.append(current_heading.strip())
    
    return new_headings

def process_text_with_summarization(pages, keywords=None):
    processed_data = []

    if keywords is None:
        keywords = ["bone marrow", "blood", "platelet", "hemoglobin", "glucose", "iron", "rbc"]

    heading_patterns = [
        re.compile(r"^CHAPTER [IVXLCDM]+[\-\.]?.*", re.IGNORECASE),
        re.compile(r"^SECTION [IVXLCDM]+.*", re.IGNORECASE),
        re.compile(r"^[A-Z]+[\-\.]?.*", re.IGNORECASE)
    ]

    for page in pages:
        page_number = page.get("page")
        text = page.get("text", "")
        
        # Split the text into paragraphs
        paragraphs = split_into_paragraphs(text)
        
        headings = []
        highlighted_text = []
        summary_sentences = []

        for paragraph in paragraphs:
            # Split paragraph into sentences
            sentences = split_into_sentences(paragraph)
            
            for sentence in sentences:
                stripped_sentence = sentence.strip()
                
                # Check if the line matches any heading pattern
                for pattern in heading_patterns:
                    if pattern.match(stripped_sentence):
                        # Split long headings
                        headings.extend(split_long_headings(stripped_sentence))
                        break

                # Highlight keywords
                for keyword in keywords:
                    keyword_pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
                    stripped_sentence = keyword_pattern.sub(f"**{keyword}**", stripped_sentence)

                highlighted_text.append(stripped_sentence)

                # Add to summary if it contains key information
                if len(stripped_sentence.split()) > 8 and any(kw in stripped_sentence.lower() for kw in keywords):
                    summary_sentences.append(stripped_sentence)

        # Ensure a summary is always present, even if no relevant keywords are found
        if not summary_sentences:
            summary_sentences.append("No relevant information found.")
        
        processed_data.append({
            "page": page_number,
            "headings": headings,
            "text": " ".join(highlighted_text),
            "summary": " ".join(summary_sentences[:3])  # Limit to 3 summary sentences per page
        })

    return processed_data

# Read input JSON file
def read_input_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Write output JSON file
def write_output_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Main function to process data
def process_json_data(input_file, output_file):
    pages = read_input_json(input_file)
    processed_data = process_text_with_summarization(pages)
    write_output_json(output_file, processed_data)

# Example usage:
input_file = './output/cleaned_data_2.json'  # Path to your input JSON file
output_file = './output/orderd_data.json'  # Path to your output JSON file
process_json_data(input_file, output_file)
