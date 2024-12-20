import re
import json
from spellchecker import SpellChecker

# Initialize spell checker
spell = SpellChecker()

# Step 1: Load input JSON data
input_file = "./output/output_data.json"
with open(input_file, "r") as file:
    data = json.load(file)

# Step 2: Remove empty pages
data = [entry for entry in data if entry['text'].strip()]

# Step 3: Remove non-relevant sections (e.g., Table of Contents, List of Figures)
non_relevant_keywords = ["table of contents", "list of figures"]
data = [
    entry for entry in data
    if not any(keyword in entry['text'].lower() for keyword in non_relevant_keywords)
]

# Step 4: Correct garbled text using spell checker
def correct_text(text):
    words = text.split()
    corrected_words = [spell.correction(word) if spell.unknown([word]) else word for word in words]
    corrected_words = [word for word in corrected_words if word is not None]  # Filter out None
    return " ".join(corrected_words)

data = [{"page": entry["page"], "text": correct_text(entry["text"])} for entry in data]

# Step 5: Standardize formatting (remove extra spaces, normalize capitalization)
def standardize_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text.strip().capitalize()

data = [{"page": entry["page"], "text": standardize_text(entry["text"])} for entry in data]

# Step 6: Save cleaned data to a new JSON file
output_file = "./output/cleaned_data_2.json"
with open(output_file, "w") as file:
    json.dump(data, file, indent=4)

print(f"Cleaned data saved to {output_file}")
