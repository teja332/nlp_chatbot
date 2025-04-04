import speech_recognition as sr
import pyttsx3
import time

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text.lower()
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return ""
        except sr.RequestError:
            print("Could not request results, please check your internet connection.")
            return ""

def chatbot():
    speak("Hello! How can I help you today?")
    while True:
        user_input = recognize_speech()
        if "exit" in user_input or "bye" in user_input:
            speak("Goodbye! Have a great day.")
            break
        elif "your name" in user_input:
            speak("I am your voice assistant.")
        elif "time" in user_input:
            current_time = time.strftime("%I:%M %p")
            speak(f"The current time is {current_time}")
        elif "date" in user_input:
            current_date = time.strftime("%B %d, %Y")
            speak(f"Today's date is {current_date}")
        else:
            speak("I am not sure how to respond to that. Can you ask something else?")

if __name__ == "__main__":
    chatbot()
