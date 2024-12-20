# sample feed forward networks 
# Sample text dataset
texts = [
    "I love this movie",    # Positive
    "This film is terrible", # Negative
    "Amazing experience",    # Positive
    "Worst movie ever",      # Negative
    "Enjoyed every moment",  # Positive
    "I hate this",           # Negative
]

# Labels (1 for positive, 0 for negative)
labels = [1, 0, 1, 0, 1, 0]

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Tokenize and convert to sequences
tokenizer = Tokenizer(num_words=100)  # Top 100 words
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)

# Pad sequences
padded_sequences = pad_sequences(sequences, maxlen=5, padding="post")
print("Padded Sequences:\n", padded_sequences)

# Check that the sequences match the expected output
expected_padded_sequences = [
    [2, 4, 1, 3, 0],
    [1, 5, 6, 7, 0],
    [8, 9, 0, 0, 0],
    [10, 3, 11, 0, 0],
    [12, 13, 14, 0, 0],
    [2, 15, 1, 0, 0]
]
assert (padded_sequences == expected_padded_sequences).all(), "Padded sequences do not match!"

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, Flatten

# Model parameters
vocab_size = len(tokenizer.word_index) + 1  # Include padding (index 0)
embedding_dim = 8  # Size of the word embeddings
input_length = 5  # Length of padded sequences

# Build the model
model = Sequential([
    Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=input_length),  # Embedding layer
    Flatten(),  # Flatten the embedding output
    Dense(10, activation="relu"),  # Hidden layer
    Dense(1, activation="sigmoid")  # Output layer (binary classification)
])

# Compile the model
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

model.build((None, 5)) 
print(model.summary())

import numpy as np

# Convert labels to numpy array
labels = np.array(labels)

# Train the model
model.fit(padded_sequences, labels, epochs=10, verbose=1)

# New sentences
new_texts = ["I really enjoyed this", "This was the worst experience"]
new_sequences = tokenizer.texts_to_sequences(new_texts)
new_padded = pad_sequences(new_sequences, maxlen=5, padding="post")

# Predict sentiment
predictions = model.predict(new_padded)
print("Predictions:", predictions)
