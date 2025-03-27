from flask import Flask, request, jsonify, render_template
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import requests
import os
from urllib.parse import urljoin, urlparse
import re

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Global variable to store all scraped content
context_data = []

# Preprocessing function
def preprocess_text(text):
    """Clean and preprocess the text."""
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespaces
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    return text.strip()

# Recursive web scraping function using requests
def scrape_full_website(url, visited=None):
    if visited is None:
        visited = set()

    if url in visited:
        return

    visited.add(url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        text = soup.get_text(separator=' ', strip=True)
        context_data.append(preprocess_text(text))

        # Find and recursively scrape all internal links
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            if urlparse(full_url).netloc == urlparse(url).netloc:
                scrape_full_website(full_url, visited)
    except Exception as e:
        print(f"Failed to scrape {url}: {str(e)}")

# Load and scrape website content
def load_full_website_content():
    content_file = "data/full_website_content.txt"
    if os.path.exists(content_file):
        # Load pre-saved content if available
        with open(content_file, "r", encoding="utf-8") as file:
            global context_data
            context_data = file.read().split("\n\n")
    else:
        # Developer's URL (start point for crawling)
        url = "https://firefox672.github.io/chatbot_exp/"  # Replace with your target URL
        scrape_full_website(url)
        # Save all content for future use
        os.makedirs("data", exist_ok=True)
        with open(content_file, "w", encoding="utf-8") as file:
            file.write("\n\n".join(context_data))

# Initialize context by loading website content
load_full_website_content()

# Load sentence transformer model for semantic similarity
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize QA pipeline for extracting answers
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Function to find relevant context
def find_relevant_context(question):
    """Find the most relevant context for the question."""
    question_embedding = embedding_model.encode(question, convert_to_tensor=True)
    context_embeddings = embedding_model.encode(context_data, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(question_embedding, context_embeddings)
    best_score_idx = scores.argmax().item()
    best_score = scores[0][best_score_idx].item()
    return context_data[best_score_idx], best_score

# Define routes
@app.route("/")
def home():
    """Serve the HTML chatbot interface."""
    return render_template("index.html")

@app.route("/chatbot", methods=["POST"])
def chatbot():
    """Chatbot route to handle user questions."""
    if not context_data:
        return jsonify({"error": "Website content could not be loaded."}), 500

    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    # Preprocess the question
    question = preprocess_text(question)

    # Find the most relevant context
    relevant_context, relevance_score = find_relevant_context(question)

    # If the relevance score is low, inform the user
    if relevance_score < 0.3:  # Adjust threshold as needed
        return jsonify({"answer": "Your question doesn't seem to be related to the website content. Please ask something relevant."})

    # Extract the answer from the relevant context
    try:
        answer = qa_pipeline(question=question, context=relevant_context)
        if not answer.get('answer') or answer.get('score', 0) < 0.5:
            return jsonify({"answer": "I'm not confident about the answer. Please rephrase or ask something else."})
    except Exception as e:
        return jsonify({"answer": f"Sorry, I couldn't process your question. Error: {str(e)}"})

    return jsonify({"answer": answer['answer']})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
