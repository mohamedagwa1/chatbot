import json
import spacy
from collections import Counter
from nltk.corpus import stopwords
import nltk
from spacy.matcher import Matcher

# Ensure stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK stopwords...")
    nltk.download('stopwords')

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Load JSON data from file
with open('./output/cleaned_data_2.json', 'r') as file:
    json_data = json.load(file)

# Synonym normalization dictionary
synonym_dict = {
    "red blood cell": "rbc",
    "white blood cell": "wbc",
    "platelets": "platelet",
    "bone marrow": "bone_marrow",
}

# Generic scientific stop terms
scientific_stop_terms = {"synthesis", "production", "process", "function", "system"}

# Preprocessing text and extracting keywords
def extract_keywords(json_data):
    stop_words = set(stopwords.words("english"))  # Load English stopwords
    # Custom stop phrases to exclude
    custom_stop_phrases = {
        'the body', 'this chapter', 'chapter', 'the liver', 
        'the bone marrow', 'the cell', 'first', 'one', 'two'
    }
    keywords = []

    # Matcher for multi-word expressions
    matcher = Matcher(nlp.vocab)
    multiword_patterns = [
        [{"LOWER": "red"}, {"LOWER": "blood"}, {"LOWER": "cell"}],
        [{"LOWER": "white"}, {"LOWER": "blood"}, {"LOWER": "cell"}],
        [{"LOWER": "bone"}, {"LOWER": "marrow"}],
        [{"LOWER": "blood"}, {"LOWER": "vessel"}],
    ]
    for pattern in multiword_patterns:
        matcher.add("KEY_PHRASES", [pattern])

    for page in json_data:
        text = page["text"]
        # Process text with spaCy
        doc = nlp(text)
        
        # Extract multi-word matches
        matches = matcher(doc)
        for match_id, start, end in matches:
            phrase = doc[start:end].text.lower()
            keywords.append(synonym_dict.get(phrase, phrase))  # Normalize synonyms
        
        # Extract noun chunks and lemmatize
        words = [
            chunk.lemma_.lower() for chunk in doc.noun_chunks
            if chunk.text.lower() not in stop_words
            and chunk.lemma_.lower() not in custom_stop_phrases
            and chunk.lemma_.lower() not in scientific_stop_terms
            and len(chunk.lemma_) > 1  # Exclude single-character words
        ]
        
        # Extract entities and lemmatize
        entities = [
            ent.lemma_.lower() for ent in doc.ents
            if ent.lemma_.lower() not in custom_stop_phrases
            and ent.lemma_.lower() not in scientific_stop_terms
        ]
        
        # Normalize synonyms
        normalized_words = [synonym_dict.get(word, word) for word in (words + entities)]
        keywords.extend(normalized_words)

    # Count the most common keywords
    keyword_counts = Counter(keywords)
    # Remove numerical keywords
    filtered_keywords = [(kw, freq) for kw, freq in keyword_counts.items() if not kw.isdigit()]
    return sorted(filtered_keywords, key=lambda x: x[1], reverse=True)[:20]  # Top 20 keywords

# Run keyword extraction
keywords = extract_keywords(json_data)

# Output extracted keywords
print("Top Keywords:", keywords)
