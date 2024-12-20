import spacy
import json

# Load the pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to preprocess the text and extract entities
def preprocess_text(text):
    doc = nlp(text)
    
    # Tokenization, removing stop words, and lemmatization
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    
    # Named Entity Recognition (NER)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    return tokens, entities

# Load input data from a JSON file
with open('./output/cleaned_data_2.json', 'r') as infile:
    data = json.load(infile)

# Process the entire JSON data
processed_data = []
for entry in data:
    page = entry["page"]
    text = entry["text"]
    
    # Apply preprocessing
    tokens, entities = preprocess_text(text)
    
    # Store the results
    processed_data.append({
        "page": page,
        "tokens": tokens,
        "entities": entities
    })

# Save the processed data to an output file
with open('./output/processed_data.json', 'w') as outfile:
    json.dump(processed_data, outfile, indent=4)

# Optionally, print the processed data
print(json.dumps(processed_data, indent=4))
