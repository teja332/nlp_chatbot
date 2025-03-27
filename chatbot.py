from flask import Flask, request, jsonify, render_template
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Function to Call Google Gemini API
def get_gemini_response(user_input):
    api_key = 'AIzaSyDW4pQUWVDZffga7ErctjK7RLfdM8-TKOo'  # Replace with your actual API key
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": user_input}
                ]
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_json = response.json()
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        return "Sorry, I don't have an answer for that question."
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Load Training Data from JSON File
def load_training_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'faq' in data:
        return data['faq']
    raise ValueError("Invalid JSON format: Expected a dictionary with a 'faq' key containing a list of questions and answers.")

# Function to Find an Answer in the JSON Training Data
def find_answer(training_data, user_question):
    for entry in training_data:
        if user_question.lower() == entry['question'].lower():
            return entry['answer']
    return "Sorry, I don't have an answer for that question."

# Root Route
@app.route('/')
def index():
    return render_template('chatbot.html')

@app.route('/about')
def about_us():
    return render_template('about_us.html')

# Route for the Chatbot
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        # Call Google Gemini API for a response
        response = get_gemini_response(user_input)

        # Return the generated response
        return jsonify({"answer": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialize the Flask App
if __name__ == '__main__':
    app.run(debug=True)
