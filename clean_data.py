import re
import json

def clean_text(text):
    # Step 1: Remove unwanted newline characters, excessive spaces, and broken words
    text = text.replace("\n", " ").replace("  ", " ").strip()

    # Step 2: Remove excessive characters like repeated 'c', 'e', and other random patterns
    text = re.sub(r'(.)\1{2,}', r'\1', text)  # reduces excessive character repetition

    # Step 3: Remove unwanted special characters that are non-informative (like 'e' or 'c' repeating)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # removes non-ASCII characters (except essential ones)

    # Step 4: Normalize multiple spaces into a single space
    text = re.sub(r'\s+', ' ', text)

    # Step 5: Convert to lowercase to standardize text for processing
    text = text.lower()

    return text

def clean_json_data(json_data):
    cleaned_data = []
    
    for entry in json_data:
        cleaned_entry = {
            "page": entry["page"],
            "text": clean_text(entry["text"])
        }
        cleaned_data.append(cleaned_entry)
    
    return cleaned_data

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# Example usage:
input_file = './output/output_data.json'  # Path to the input JSON file
output_file = './output/cleaned_output_data.json'  # Path to the output cleaned JSON file

# Load the raw data from the input file
raw_json = load_json(input_file)

# Clean the JSON data
cleaned_json = clean_json_data(raw_json)

# Save the cleaned data to the output file
save_json(cleaned_json, output_file)

print(f"Cleaned data saved to {output_file}")
