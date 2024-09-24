from flask import Flask, jsonify
import speech_recognition as sr
from groq import Groq
import pygame
import threading
from datetime import datetime
import pyttsx3

app = Flask(__name__)

class SpeechAssistant:
    def __init__(self):
        self.running = False
        self.client = Groq(api_key="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")
        self.initialize_services()

    def initialize_services(self):
        pygame.mixer.init()

    def speak(self, text):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if "Zira" in voice.name:
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        engine.runAndWait()

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.running:
                print("Listening for command...")
                audio = recognizer.listen(source)

                try:
                    command = recognizer.recognize_google(audio, language='en-US')
                    if not command:
                        raise ValueError("Empty text recognized.")
                except sr.UnknownValueError:
                    print("I couldn't understand what you said.")
                    continue
                except sr.RequestError as e:
                    print(f"Error in the recognition service request: {e}")
                    continue

                self.process_command(command)

    def process_command(self, command):
        print(f"USER: {command}")

        if command.lower() == "what time is it":
            current_time = datetime.now().strftime("%H:%M")
            response = f"The current time is {current_time}."
            print(response)
            threading.Thread(target=self.speak, args=(response,)).start()
        elif command.lower() == "exit":
            print("Stopping the program.")
            threading.Thread(target=self.speak, args=("Stopping the program.",)).start()
            self.running = False
        else:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You're a useful assistant called S1. be super-short and polite."
                        },
                        {
                            "role": "user",
                            "content": command
                        }
                    ],
                    model="llama3-8b-8192",
                    temperature=0.5,
                    max_tokens=1024,
                    top_p=1,
                    stream=False
                )

                chatbot_response = chat_completion.choices[0].message.content
                print(chatbot_response)
                threading.Thread(target=self.speak, args=(chatbot_response,)).start()

            except Exception as e:
                print(f"Error processing the chatbot response: {e}")
                threading.Thread(target=self.speak, args=("Sorry, but there was an error processing your request.",)).start()

    def start(self):
        self.running = True
        threading.Thread(target=self.recognize_speech).start()

    def stop(self):
        self.running = False


assistant = SpeechAssistant()

@app.route('/start', methods=['POST'])
def start_listening():
    assistant.start()
    return jsonify({"message": "Listening started!"}), 200

@app.route('/stop', methods=['POST'])
def stop_listening():
    assistant.stop()
    return jsonify({"message": "Listening stopped!"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=9099)
