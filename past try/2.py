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
from tensorflow.keras.layers import SimpleRNN, Dense, Embedding

# Model parameters
vocab_size = len(tokenizer.word_index) + 1  # Include padding (index 0)
embedding_dim = 8
input_length = 5  # Length of padded sequences

# Build the RNN model
model = Sequential([
    Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=input_length),  # Embedding layer
    SimpleRNN(16, activation="tanh"),  # RNN layer with 16 units
    Dense(1, activation="sigmoid")  # Output layer for binary classification
])

# Compile the model
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

model.build((None, 5)) 

print(model.summary())

# Train the model
import numpy as np

# Convert labels to a NumPy array
labels = np.array(labels)

model.fit(padded_sequences, labels, epochs=10, verbose=1)



# Predict sentiment for new sentences
new_texts = ["I absolutely loved it", "I did not like it at all"]
new_sequences = tokenizer.texts_to_sequences(new_texts)
new_padded = pad_sequences(new_sequences, maxlen=5, padding="post")

predictions = model.predict(new_padded)
print("Predictions:", predictions)

