from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- Import CORS
import spacy
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from transformers import pipeline
import os
from sklearn.metrics.pairwise import cosine_similarity

# Initialize the app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Load pre-trained models
nlp = spacy.load("en_core_web_sm")  # General-purpose spaCy model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Embedding model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  # Summarization pipeline

# Paths for data and precomputed embeddings
DATA_PATH = "./output/cleaned_data_2.json"
EMBEDDINGS_PATH = "./output/data_embeddings.npy"
INDEX_PATH = "./output/faiss_index.bin"

# Load book data
with open(DATA_PATH, "r") as file:
    data = json.load(file)

# Precompute or load embeddings
texts = [page["text"] for page in data]

if not os.path.exists(EMBEDDINGS_PATH) or not os.path.exists(INDEX_PATH):
    print("Precomputing embeddings and creating FAISS index...")
    embeddings = model.encode(texts)
    np.save(EMBEDDINGS_PATH, embeddings)
    
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    faiss.write_index(index, INDEX_PATH)
else:
    print("Loading precomputed embeddings and FAISS index...")
    embeddings = np.load(EMBEDDINGS_PATH)
    index = faiss.read_index(INDEX_PATH)

# Extract keywords using spaCy
def extract_keywords(question):
    doc = nlp(question)
    keywords = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    keywords.extend([ent.text for ent in doc.ents if ent.label_ in ['ORG', 'GPE', 'PERSON']])
    return ' '.join(set(keywords))

# Search for answers in FAISS index
def search_answer(query, top_k=3):
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    return [(texts[i], distances[0][idx]) for idx, i in enumerate(indices[0])]

# Filter responses by similarity threshold
def filter_relevant_results(results, threshold=0.9):
    filtered_results = []
    for res in results:
        text, score = res
        # Check if all the words "This", "discusses", and "chapter" are present in the text
        if all(word.lower() in text.lower() for word in ["This", "discusses", "chapter"]) and score > threshold:
            continue  # Skip this result if all words are found in the paragraph
        filtered_results.append(res)
    return filtered_results


# Combine responses into a cohesive summary
def combine_responses(results):
    combined_text = " ".join([res[0] for res in results])
    summarized_text = summarizer(combined_text, max_length=200, min_length=100, do_sample=False)[0]['summary_text']
    return summarized_text

# Format the final answer
# can be ai 
def format_answer(results, threshold=0.9):
    relevant_results = filter_relevant_results(results, threshold)
    
    if relevant_results:
        final_answer = combine_responses(relevant_results)
        return f"Answer: {final_answer}\n"
    else:
        return "The information found does not provide a clear answer. Please try rephrasing the question."

# Chatbot function
def chatbot(question):
    keywords = extract_keywords(question)
    results = search_answer(keywords)
    return format_answer(results)

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json['question']
    response = chatbot(user_question)
    return jsonify({'answer': response})

if __name__ == '__main__':
    app.run(debug=True)



# Mention signs, symptoms and treatment of porphyria.