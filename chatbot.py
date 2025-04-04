from flask import Flask, request, jsonify, render_template
import json
from flask_cors import CORS
from vosk import Model, KaldiRecognizer
import pyaudio
from fuzzywuzzy import process

app = Flask(__name__)
CORS(app)

# Load Training Data
training_data = []

def load_training_data(filepath):
    global training_data
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'faq' in data:
        training_data = data['faq']
    else:
        raise ValueError("Invalid JSON format: Expected a dictionary with a 'faq' key.")

def find_answer(user_question):
    # Use fuzzy matching to find the best match from the training data.
    questions = [entry['question'] for entry in training_data]
    best_match, score = process.extractOne(user_question.lower(), questions)
    
    # If the fuzzy match score is above 70, return the corresponding answer.
    if score > 70:
        return next(entry['answer'] for entry in training_data if entry['question'] == best_match)
    
    # Otherwise, attempt to find a related topic by checking for common words.
    user_words = set(user_question.lower().split())
    best_candidate = None
    best_overlap = 0
    for entry in training_data:
        entry_words = set(entry['question'].lower().split())
        overlap = len(user_words.intersection(entry_words))
        if overlap > best_overlap:
            best_overlap = overlap
            best_candidate = entry
    if best_candidate and best_overlap > 0:
        return best_candidate['answer']
    
    return "Sorry, I don't have an answer for that."

load_training_data('training_data.json')

# Offline Speech Recognition
model = Model("model")
recognizer = KaldiRecognizer(model, 16000)

def recognize_speech_offline():
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    while True:
        data = stream.read(4096)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            return result.get("text", "")

@app.route('/')
def index():
    return render_template('chatbot.html')

@app.route('/about')
def about_us():
    return render_template('about_us.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        response = find_answer(user_input)
        return jsonify({"answer": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/speech-recognition', methods=['GET'])
def speech_recognition():
    try:
        recognized_text = recognize_speech_offline()
        return jsonify({"transcript": recognized_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
