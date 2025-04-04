import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Load training data
def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['faq']

# Text Preprocessing
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# Load and preprocess data
faq_data = load_data('training_data.json')
questions = [preprocess_text(entry['question']) for entry in faq_data]

# Convert questions into TF-IDF vectors
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(questions)

# Save the processed data
for i, entry in enumerate(faq_data):
    entry['processed_question'] = questions[i]

with open('processed_faq.json', 'w', encoding='utf-8') as f:
    json.dump(faq_data, f, indent=4)

# Save vectorizer and vectorized questions for later use
with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

with open('vectorized_questions.pkl', 'wb') as f:
    pickle.dump(X, f)

print("Preprocessing complete. Data saved.")
