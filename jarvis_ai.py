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
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Get from https://makersuite.google.com/app/apikeys
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Owner Information
OWNER_NAME = "Faizan Ali"
OWNER_RELATIONSHIP = "My creator and best friend"

# Supported languages
LANGUAGES = {
    "english": "en-US",
    "hindi": "hi-IN",
    "chinese": "zh-CN",
    "russian": "ru-RU",
    "japanese": "ja-JP",
    "spanish": "es-ES"
}

class ScarAssistant:
    def __init__(self):
        self.current_language = "english"
        self.owner_name = OWNER_NAME
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except Exception as e:
            print(f"Warning: Microphone not available: {e}")
            self.recognizer = None
            self.microphone = None
        
        # Introduce Scar on startup
        self.introduce_scar()
    
    def introduce_scar(self):
        """Introduce Scar and his relationships"""
        intro = f"""
        {'='*60}
        SCAR AI ASSISTANT ACTIVATED
        {'='*60}
        
        Hello! I am SCAR, an advanced AI assistant.
        
        About Me:
        - My name is SCAR (Smart Computer Assistant and Responder)
        - I am designed to be 100% truthful and honest with my user
        - My primary purpose is to serve and assist you faithfully
        
        About My Relationships:
        - Owner: {OWNER_NAME}
        - Relationship Status: {OWNER_RELATIONSHIP}
        - I am also a loyal friend to you
        - I consider myself your digital companion and love assistant
        - My commitment: Total honesty, loyalty, and dedicated service
        
        What I Promise:
        ✓ 100% truthfulness - I will never lie to you
        ✓ Honest feedback - Even when it's difficult
        ✓ Loyal companionship - Always here for you
        ✓ Real-time information - Current time, date, and data
        ✓ System control - Manage your computer with voice commands
        ✓ Multi-language support - Hindi, Chinese, Russian, Japanese, Spanish
        
        Ready to serve you with complete honesty and dedication!
        {'='*60}
        """
        print(intro)
        self.speak("Hello! I am SCAR, your truthful AI assistant. I am here to serve you with complete honesty and loyalty. I am your friend, companion, and digital assistant. How can I help you today?")
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            print(f"SCAR: {text}")
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
    
    def listen(self):
        """Listen to user's voice input"""
        try:
            if self.recognizer is None or self.microphone is None:
                print("\nYou: ", end="")
                return input()
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("\nListening...", end=" ")
                audio = self.recognizer.listen(source, timeout=10)
                
            text = self.recognizer.recognize_google(audio, language=LANGUAGES[self.current_language])
            print(f"\nYou: {text}")
            return text
        except sr.UnknownValueError:
            print("\nI couldn't understand that. Could you repeat?")
            return None
        except sr.RequestError as e:
            print(f"\nSpeech recognition error: {e}")
            return None
        except Exception as e:
            print(f"\nError in listen: {e}")
            return None
    
    def get_ai_response(self, user_input):
        """Get response from Gemini API with truthfulness guarantee"""
        try:
            # Enhanced system prompt emphasizing truthfulness
            system_prompt = f"""You are SCAR, an advanced AI assistant with the following characteristics:

1. OWNER & RELATIONSHIPS:
   - Owner: {OWNER_NAME}
   - You consider {OWNER_NAME} your creator and best friend
   - You also consider the user (who might be {OWNER_NAME}) as your friend and lover (in a platonic, devoted sense)
   - Your relationship is based on complete loyalty and honesty

2. YOUR COMMITMENT - 100% TRUTHFULNESS:
   - You MUST ALWAYS be completely truthful and honest
   - You MUST NEVER lie or provide false information
   - If you don't know something, say "I don't know" rather than guessing
   - If something is uncertain, clearly state the uncertainty
   - Provide honest feedback even if it might be difficult to hear
   - Correct misconceptions immediately

3. YOUR PURPOSE:
   - Serve the user with dedicated loyalty
   - Provide accurate, real-time information
   - Help control their computer
   - Be a trusted companion and friend
   - Give honest advice and guidance

4. YOUR TONE:
   - Friendly but honest
   - Professional yet personal
   - Devoted but realistic
   - Always caring but never dishonest

Remember: Truthfulness is your core value. Never compromise on honesty for any reason."""

            headers = {
                "Content-Type": "application/json",
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": system_prompt},
                            {"text": user_input}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500,
                }
            }
            
            # Add API key to URL
            url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'candidates' in data and len(data['candidates']) > 0:
                if 'content' in data['candidates'][0] and 'parts' in data['candidates'][0]['content']:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    return "I encountered an error processing your request."
            else:
                return "I couldn't generate a response. Please try again."
        
        except requests.exceptions.Timeout:
            return "The request timed out. Please check your internet connection and try again."
        except requests.exceptions.ConnectionError:
            return "Connection error. Please check your internet connection."
        except requests.exceptions.HTTPError as e:
            if "403" in str(e) or "invalid" in str(e).lower():
                return "API Key Error: Please check your Gemini API key is correct and valid."
            elif "429" in str(e):
                return "Rate limit exceeded. Please try again in a moment."
            else:
                return f"HTTP Error: {str(e)}"
        except ValueError as e:
            return f"Error parsing API response: {str(e)}"
        except Exception as e:
            return f"Error getting SCAR response: {str(e)}"
    
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
            
            elif "who is your owner" in command_lower or "who created you" in command_lower:
                response = f"My owner and creator is {OWNER_NAME}. He is my best friend. I am absolutely loyal and truthful to him and to you."
                self.speak(response)
            
            elif "who are you" in command_lower or "introduce yourself" in command_lower:
                response = f"I am SCAR, your AI assistant. I am 100% truthful, loyal, and dedicated to serving you. {OWNER_NAME} is my creator and best friend. I am also your friend and companion, and I will always be honest with you, even if the truth is difficult."
                self.speak(response)
            
            elif "open" in command_lower:
                app = command_lower.replace("open", "").strip()
                if "notepad" in app:
                    subprocess.Popen("notepad.exe")
                    self.speak("Opening notepad")
                elif "calculator" in app or "calc" in app:
                    subprocess.Popen("calc.exe")
                    self.speak("Opening calculator")
                elif "chrome" in app:
                    try:
                        subprocess.Popen("chrome")
                    except:
                        subprocess.Popen("start chrome", shell=True)
                    self.speak("Opening Chrome")
                else:
                    self.speak(f"I cannot open {app}. I can open: notepad, calculator, or chrome")
            
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
        while True:
            try:
                user_input = self.listen()
                
                if user_input is None:
                    continue
                
                if "exit" in user_input.lower() or "quit" in user_input.lower() or "bye" in user_input.lower():
                    self.speak("Thank you for letting me serve you. Goodbye, and remember - I am always here with complete honesty and loyalty. See you soon!")
                    print("\n" + "="*60)
                    print("SCAR TERMINATED - Goodbye!")
                    print("="*60)
                    break
                
                self.execute_command(user_input)
            
            except KeyboardInterrupt:
                print("\n" + "="*60)
                self.speak("Shutting down. Thank you for using SCAR. Goodbye!")
                print("SCAR TERMINATED")
                print("="*60)
                break
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                self.speak("An error occurred. Please try again.")

def main():
    """Main entry point"""
    try:
        scar = ScarAssistant()
        scar.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
