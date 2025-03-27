let listening = false;
let speechSynthesisActive = false;
let currentLanguage = 'en-US';
const maxResponseLength = 500;

// Function to stop voice interaction and reset the microphone icon
function stopVoiceInteraction() {
    if (speechSynthesisActive) {
        window.speechSynthesis.cancel();
        speechSynthesisActive = false;
    }
    if (listening) {
        recognition.stop();
        listening = false;
        document.getElementById('voice-icon').src = '/static/mic_icon.png'; // Reset mic icon
    }
    // Enable user input and voice icon
    toggleInputField(true);
}

// Function to append messages to chat
function appendMessage(content, sender) {
    const truncatedContent = content.length > maxResponseLength
        ? content.substring(0, maxResponseLength) + '...'
        : content;

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.innerText = truncatedContent;
    document.getElementById('chat-body').appendChild(messageDiv);
    document.getElementById('chat-body').scrollTop = document.getElementById('chat-body').scrollHeight;

    // Voice Assistant - Speak the bot's response if sender is bot
    if (sender === 'bot') {
        speak(truncatedContent);
        toggleSendStopButton('showStop');
        // Disable user input and voice icon while speaking
        toggleInputField(false);
    }
}

// Function to send user messages
function sendMessage(userInput = null) {
    const userMessage = userInput || document.getElementById('user-input').value.trim();
    if (!userMessage) return;

    appendMessage(userMessage, 'user');
    document.getElementById('user-input').value = '';
    document.getElementById('user-input').focus();

    fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.answer) {
            appendMessage(data.answer, 'bot');
        } else if (data.error) {
            appendMessage("Sorry, something went wrong.", 'bot');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        appendMessage("Sorry, something went wrong.", 'bot');
    });
}

// Function to handle text-to-speech
function speak(text) {
    if (speechSynthesisActive) {
        window.speechSynthesis.cancel(); // Stop any ongoing speech synthesis
    }

    const speech = new SpeechSynthesisUtterance();
    speech.text = text;
    speech.lang = currentLanguage;
    speechSynthesisActive = true;

    speech.onend = () => {
        speechSynthesisActive = false;
        toggleSendStopButton('showSend');
        toggleInputField(true); // Enable input after speech ends
    };

    window.speechSynthesis.speak(speech);
}

// Voice Recognition Functionality
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = currentLanguage;
recognition.interimResults = true; // Enable interim results for live text updates
recognition.continuous = false;

recognition.onresult = function(event) {
    let finalTranscript = '';
    let interimTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
        } else {
            interimTranscript += event.results[i][0].transcript;
        }
    }

    // Update the "Type your message" box with interim results while user speaks
    document.getElementById('user-input').value = finalTranscript + interimTranscript;

    // Send final transcript as message when user stops speaking
    if (finalTranscript) {
        sendMessage(finalTranscript);
        document.getElementById('user-input').value = ''; // Clear input box
        listening = false;
        document.getElementById('voice-icon').src = '/static/mic_icon.png';
    }
};

recognition.onspeechend = function() {
    if (listening) {
        recognition.stop();
        listening = false;
        document.getElementById('voice-icon').src = '/static/mic_icon.png';
    }
};

recognition.onerror = function(event) {
    console.error('Speech recognition error detected:', event.error);
    listening = false;
    document.getElementById('voice-icon').src = '/static/mic_icon.png';
    appendMessage("Sorry, speech recognition error occurred.", 'bot');
};

// Handle voice icon click for starting/stopping speech recognition
document.getElementById('voice-icon').addEventListener('click', function() {
    if (listening) {
        recognition.stop();
        listening = false;
        document.getElementById('voice-icon').src = '/static/mic_icon.png'; // Reset mic icon
        toggleInputField(true); // Enable input when stopping
    } else {
        if (speechSynthesisActive) {
            window.speechSynthesis.cancel(); // Stop ongoing speech synthesis if any
        }
        appendMessage("Listening...", 'bot');
        recognition.start();
        listening = true;
        document.getElementById('voice-icon').src = '/static/mic_icon_active.png'; // Change mic icon to show active listening
        toggleInputField(false); // Disable input while listening
    }
});

// Function to stop speaking when stop button is clicked
function stopSpeaking() {
    stopVoiceInteraction();
    toggleSendStopButton('showSend');
}

// Toggle between Send and Stop buttons
function toggleSendStopButton(action) {
    const sendButton = document.getElementById('send-button');
    const stopButton = document.getElementById('stop-button');

    if (action === 'showStop') {
        sendButton.style.display = 'none';
        stopButton.style.display = 'inline';
    } else {
        stopButton.style.display = 'none';
        sendButton.style.display = 'inline';
    }
}

// Toggle input field's disabled state
function toggleInputField(isEnabled) {
    const userInput = document.getElementById('user-input');
    userInput.disabled = !isEnabled;
}

// Handle Enter key for sending messages
document.getElementById('user-input').addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Focus on user input on page load
window.onload = function() {
    document.getElementById('user-input').focus();
};
