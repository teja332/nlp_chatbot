import requests

# Define the URL of your Flask server
url = 'http://127.0.0.1:5000/chatbot'

# Create the data payload with the message you want to send
data = {'message': 'How does the chatbot work?'}

# Send a POST request to the server
response = requests.post(url, json=data)

# Print the raw response text
print('Raw Server Response:', response.text)

try:
    # Attempt to parse JSON response
    print('Parsed JSON Response:', response.json())
except requests.exceptions.JSONDecodeError:
    print('Failed to parse JSON, raw response text:', response.text)
