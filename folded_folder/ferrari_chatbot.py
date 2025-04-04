from flask import Flask, request, jsonify, render_template
from transformers import pipeline, DistilBertTokenizer, DistilBertForQuestionAnswering
import sqlite3
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize Database
def init_db():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS qa (question TEXT, answer TEXT)''')
    conn.commit()
    conn.close()

# Store Q&A in Database
def store_qa(question, answer):
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute("INSERT INTO qa (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()

# Load Pre-trained Model and Tokenizer
model = DistilBertForQuestionAnswering.from_pretrained('distilbert-base-cased-distilled-squad')
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-cased-distilled-squad')
qa_pipeline = pipeline('question-answering', model=model, tokenizer=tokenizer)

# Define common responses
common_responses = {
    "hello": "Hello! How can I assist you today?",
    "hi": "Hi there! How can I help?",
    "how are you": "I'm here and ready to assist you with any information you need.",
    "what is your name": "I'm the Ferrari Chatbot, your knowledgeable assistant!",
    "bye": "Goodbye! Reach out anytime you need help."
}

# List of URLs to scrape content from
website_urls = [
    "https://firefox672.github.io/chatbot_exp/",
    # Add more URLs here as needed
]

# Fetch content from multiple websites
def fetch_website_content():
    combined_context = ""
    for url in website_urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text(separator=" ", strip=True)
                combined_context += page_text + " "
        except Exception as e:
            print(f"Failed to fetch content from {url}: {e}")
    
    return combined_context

# General web scraping function for more targeted queries
def fetch_general_info(query):
    search_url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            for paragraph in paragraphs:
                text = paragraph.get_text().strip()
                if len(text) > 50:
                    return text
        return "I'm unable to find detailed information on that topic right now."
    except Exception as e:
        return f"An error occurred while searching for information: {e}"

# Route for the Chat Interface
@app.route('/')
def index():
    return render_template("index.html")

# Route for Chatbot Interaction
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    normalized_input = user_input.lower().strip()

    # Check for a predefined common response
    if normalized_input in common_responses:
        response = common_responses[normalized_input]
        return jsonify({"answer": response})

    try:
        # Check database for previously stored answer
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        c.execute("SELECT answer FROM qa WHERE question=?", (user_input,))
        stored_answer = c.fetchone()
        conn.close()

        if stored_answer:
            return jsonify({"answer": stored_answer[0]})

        # Fetch content from multiple websites
        context = fetch_website_content()
        response_from_sites = qa_pipeline(question=user_input, context=context)['answer']

        if response_from_sites and len(response_from_sites) > 5:
            store_qa(user_input, response_from_sites)
            return jsonify({"answer": response_from_sites})

        # If no answer found from website content, fetch general info from Wikipedia
        general_info = fetch_general_info(user_input)
        store_qa(user_input, general_info)
        return jsonify({"answer": general_info})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialize Database and Start Flask App
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
