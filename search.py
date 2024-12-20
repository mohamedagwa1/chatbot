import spacy
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from transformers import pipeline
import os

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
    """
    Extract keywords from a question using spaCy.
    """
    doc = nlp(question)
    keywords = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    # Include named entities for better medical relevance
    keywords.extend([ent.text for ent in doc.ents if ent.label_ in ['ORG', 'GPE', 'PERSON']])
    return ' '.join(set(keywords))

# Search for answers in FAISS index
def search_answer(query, top_k=3):
    """
    Perform similarity search using FAISS.
    """
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    return [(texts[i], distances[0][idx]) for idx, i in enumerate(indices[0])]

# Filter responses by similarity threshold
def filter_relevant_results(results, threshold=0.90):
    """
    Filter responses based on a similarity threshold.
    """
    return [res for res in results if res[1] > threshold]

# Combine responses into a cohesive summary
def combine_responses(results):
    """
    Combine multiple relevant responses into one cohesive summary.
    """
    combined_text = " ".join([res[0] for res in results])
    summarized_text = summarizer(combined_text, max_length=200, min_length=100, do_sample=False)[0]['summary_text']
    return summarized_text

# Format the final answer
def format_answer(results, threshold=0.90):
    """
    Format the final answer after filtering and combining responses.
    """
    # Filter results by similarity threshold
    relevant_results = filter_relevant_results(results, threshold)
    
    if relevant_results:
        # Combine and summarize filtered responses
        final_answer = combine_responses(relevant_results)
        return f"Answer: {final_answer}\n"
    else:
        return "The information found does not provide a clear answer. Please try rephrasing the question."

# Chatbot function
def chatbot(question):
    """
    Main chatbot function to handle user questions.
    """
    keywords = extract_keywords(question)
    results = search_answer(keywords)
    return format_answer(results)

# Test the chatbot
# if __name__ == "__main__":
#     user_question = "What is the function of plasma?"
#     print(chatbot(user_question))

test_cases = [
    {"query": "What is the function of plasma?", "expected": "A description of plasma's role in transport, regulation, and immunity."},
    {"query": "Tell me about plasma.", "expected": "A general explanation of plasma, distinguishing its role in biology."},
    {"query": "What are the components of plasma?", "expected": "A list or summary of plasma components such as water, proteins, ions, and hormones."},
    {"query": "What are the functions of blood?", "expected": "A detailed explanation of blood's transport, regulatory, and protective roles."},
    {"query": "What are the symptoms of anemia?", "expected": "A clear list of symptoms such as fatigue, pallor, and shortness of breath."},
    {"query": "Explain pl@sm@ in human bod!y.", "expected": "A relevant answer about plasma despite the noisy input."},
    {"query": "What is the capital of France?", "expected": "A response indicating the information is unrelated to the dataset."},
    {"query": "How does plasma contribute to blood clotting?", "expected": "Explanation highlighting plasma proteins involved in clotting."},
    {"query": "Define albumin and its role in plasma.", "expected": "A concise definition of albumin and its roles."},
    {"query": "Explain in detail the functions of plasma, its components, and their roles in maintaining homeostasis in the human body.", 
     "expected": "A detailed summary with no performance degradation."}
]

for i, test in enumerate(test_cases, 1):
    print(f"Test Case {i}: {test['query']}")
    response = chatbot(test["query"])
    print(f"Response: {response}")
    print("-" * 80)