import os
import requests
import json
import pyttsx3
import speech_recognition as sr
from datetime import datetime
import subprocess
import sys

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# Configuration
AI_API_KEY = "YOUR_AI_API_KEY"  # Get your API key from your AI provider
AI_API_URL = "https://api.openai.com/v1/chat/completions"  # Replace with your AI provider's endpoint

# Supported languages
LANGUAGES = {
    "english": "en-US",
    "hindi": "hi-IN",
    "chinese": "zh-CN",
    "russian": "ru-RU",
    "japanese": "ja-JP",
    "spanish": "es-ES"
}

class JarvisAssistant:
    def __init__(self):
        self.current_language = "english"
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except Exception as e:
            print(f"Warning: Microphone not available: {e}")
            self.recognizer = None
            self.microphone = None
        
    def speak(self, text):
        """Convert text to speech"""
        try:
            print(f"Jarvis: {text}")
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
    
    def listen(self):
        """Listen to user's voice input"""
        try:
            if self.recognizer is None or self.microphone is None:
                print("Microphone not available. Enter text instead:")
                return input("You: ")
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=10)
                
            text = self.recognizer.recognize_google(audio, language=LANGUAGES[self.current_language])
            print(f"You: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"Error in listen: {e}")
            return None
    
    def get_ai_response(self, user_input):
        """Get response from AI API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {AI_API_KEY}"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are Jarvis, a helpful AI assistant for controlling a computer. Keep responses concise and friendly. Provide real-time information when asked."},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(AI_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            else:
                return "I encountered an error processing your request."
        
        except requests.exceptions.Timeout:
            return "The request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "Connection error. Please check your internet connection."
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                return "Authentication failed. Please check your API key."
            elif response.status_code == 429:
                return "Rate limit exceeded. Please try again later."
            else:
                return f"HTTP Error: {response.status_code}"
        except ValueError:
            return "Invalid response from AI API. Please check your configuration."
        except Exception as e:
            return f"Error getting AI response: {str(e)}"
    
    def execute_command(self, command):
        """Execute system commands"""
        try:
            command_lower = command.lower()
            
            if "time" in command_lower:
                current_time = datetime.now().strftime("%H:%M:%S")
                response = f"The current time is {current_time}"
                self.speak(response)
            
            elif "date" in command_lower:
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                response = f"Today is {current_date}"
                self.speak(response)
            
            elif "open" in command_lower:
                app = command_lower.replace("open", "").strip()
                if "notepad" in app:
                    subprocess.Popen("notepad.exe")
                    self.speak(f"Opening notepad")
                elif "calculator" in app or "calc" in app:
                    subprocess.Popen("calc.exe")
                    self.speak(f"Opening calculator")
                elif "chrome" in app:
                    try:
                        subprocess.Popen("chrome")
                    except:
                        subprocess.Popen("start chrome", shell=True)
                    self.speak(f"Opening Chrome")
                else:
                    self.speak(f"I don't know how to open {app}")
            
            elif "change language" in command_lower:
                language_changed = False
                for lang in LANGUAGES:
                    if lang in command_lower:
                        self.current_language = lang
                        self.speak(f"Language changed to {lang}")
                        language_changed = True
                        break
                if not language_changed:
                    self.speak("Please specify a language: English, Hindi, Chinese, Russian, Japanese, or Spanish")
            
            else:
                response = self.get_ai_response(command)
                self.speak(response)
        
        except subprocess.CalledProcessError as e:
            self.speak(f"Error executing command: {str(e)}")
        except Exception as e:
            self.speak(f"Error: {str(e)}")
    
    def run(self):
        """Main loop"""
        print("=" * 50)
        print("JARVIS AI ASSISTANT STARTED")
        print("=" * 50)
        self.speak("Hello, I am Jarvis, your AI assistant. What can I help you with?")
        
        while True:
            try:
                user_input = self.listen()
                
                if user_input is None:
                    continue
                
                if "exit" in user_input.lower() or "quit" in user_input.lower() or "bye" in user_input.lower():
                    self.speak("Goodbye!")
                    print("Shutting down...")
                    break
                
                self.execute_command(user_input)
            
            except KeyboardInterrupt:
                print("\n" + "=" * 50)
                self.speak("Shutting down. Goodbye!")
                print("JARVIS TERMINATED")
                print("=" * 50)
                break
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                self.speak("An error occurred. Please try again.")

def main():
    """Main entry point"""
    try:
        jarvis = JarvisAssistant()
        jarvis.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
