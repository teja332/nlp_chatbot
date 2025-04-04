let listening = false;
let speechSynthesisActive = false;
let currentLanguage = 'en-US';
const maxResponseLength = 500;

function stopVoiceInteraction() {
    if (speechSynthesisActive) {
        window.speechSynthesis.cancel();
        speechSynthesisActive = false;
    }
    if (listening) {
        recognition.stop();
        listening = false;
        document.getElementById('voice-icon').src = '/static/mic_icon.png';
    }
    toggleInputField(true);
}

function appendMessage(content, sender) {
    const truncatedContent = content.length > maxResponseLength ? content.substring(0, maxResponseLength) + '...' : content;
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.innerText = truncatedContent;
    document.getElementById('chat-body').appendChild(messageDiv);
    document.getElementById('chat-body').scrollTop = document.getElementById('chat-body').scrollHeight;

    if (sender === 'bot') {
        speak(truncatedContent);
        toggleSendStopButton('showStop');
        toggleInputField(false);
    }
}

function sendMessage(userInput = null) {
    const userMessage = userInput || document.getElementById('user-input').value.trim();
    if (!userMessage) return;

    appendMessage(userMessage, 'user');
    document.getElementById('user-input').value = '';
    document.getElementById('user-input').focus();

    fetch('/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
    })
    .then(response => response.json())
    .then(data => {
        appendMessage(data.answer || "Sorry, something went wrong.", 'bot');
    })
    .catch(error => {
        console.error('Error:', error);
        appendMessage("Sorry, something went wrong.", 'bot');
    });
}

function speak(text) {
    if (speechSynthesisActive) {
        window.speechSynthesis.cancel();
    }

    const speech = new SpeechSynthesisUtterance();
    speech.text = text;
    speech.lang = currentLanguage;
    speechSynthesisActive = true;

    speech.onend = () => {
        speechSynthesisActive = false;
        toggleSendStopButton('showSend');
        toggleInputField(true);
    };

    window.speechSynthesis.speak(speech);
}

const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = currentLanguage;
recognition.interimResults = true;
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

    document.getElementById('user-input').value = finalTranscript + interimTranscript;
};

recognition.onspeechend = function() {
    if (listening) {
        recognition.stop();
        listening = false;
        document.getElementById('voice-icon').src = '/static/mic_icon.png';
    }
};

recognition.onerror = function(event) {
    console.error('Speech recognition error:', event.error);
    listening = false;
    document.getElementById('voice-icon').src = '/static/mic_icon.png';
    appendMessage("Speech recognition error occurred.", 'bot');
};

document.getElementById('voice-icon').addEventListener('click', function() {
    if (listening) {
        recognition.stop();
        listening = false;
        document.getElementById('voice-icon').src = '/static/mic_icon.png';
        toggleInputField(true);
    } else {
        if (speechSynthesisActive) {
            window.speechSynthesis.cancel();
        }
        appendMessage("Listening...", 'bot');
        recognition.start();
        listening = true;
        document.getElementById('voice-icon').src = '/static/mic_icon_active.png';
        toggleInputField(false);
    }
});

function stopSpeaking() {
    stopVoiceInteraction();
    toggleSendStopButton('showSend');
}

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

function toggleInputField(isEnabled) {
    document.getElementById('user-input').disabled = !isEnabled;
}

document.getElementById('user-input').addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

window.onload = function() {
    document.getElementById('user-input').focus();
};
