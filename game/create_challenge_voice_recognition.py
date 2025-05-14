"""Module for parsing game setup voice commands"""
import speech_recognition as sr
import os
import glob
from gtts import gTTS
import pygame
import time

class ChallengeTTS:
    def __init__(self):
        # Clean up any leftover files from previous runs
        #self._cleanup_previous_files()
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        self.count = 0
        self.temp_files = []  # Track all created files
        self.temp_pattern = "temp_speech_"  # Base pattern for temp files
        self._cleanup_previous_files()
    def _cleanup_previous_files(self):
        """Clean up any leftover speech files from previous runs"""
        print("\nCleaning up any leftover TTS files...")
        
        # Find all temp speech files in the current directory
        for file in glob.glob(f"temp_speech_*.mp3"):
            try:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Removed leftover file: {file}")
            except Exception as e:
                print(f"Could not remove leftover file {file}: {e}")
                
        # Also check game directory
        game_dir = os.path.dirname(os.path.abspath(__file__))
        cwd = os.getcwd()
        if game_dir != cwd:
            for file in glob.glob(os.path.join(game_dir, f"{self.temp_pattern}*.mp3")):
                try:
                    os.remove(file)
                    print(f"Removed leftover file: {file}")
                except Exception as e:
                    print(f"Could not remove leftover file {file}: {e}")
        
    def speak(self, text):
        """Speak text using Google TTS and wait for completion"""
        print(f"\nPrompt: {text}")
        try:
            # Create sequentially numbered temp file
            temp_file = f"{self.temp_pattern}{self.count}.mp3"
            self.temp_files.append(temp_file)
            self.count += 1
            
            # Create MP3 file with Google TTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file)
            
            # Play the audio and wait for it to finish
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"Speech error: {e}")
            
    def cleanup(self):
        """Just stop the audio - we'll clean files in the next run"""
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("Audio system shutdown complete")

def get_number_from_voice(recognizer, source, tts):
    """Get a number from voice input"""
    print("\nListening for number...")
    
    try:
        audio = recognizer.listen(source, timeout=5)
        text = recognizer.recognize_google(audio).lower()
        print(f"You said: {text}")
        
        # Try to extract number
        words = text.split()
        for word in words:
            if word.isdigit():
                print(f"Found number: {word}")
                return int(word)
            # Handle spoken numbers
            number_map = {
                'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                'fifteen': 15, 'twenty': 20, 'thirty': 30,
                'zero': 0, 'oh': 0
            }
            if word in number_map:
                print(f"Found number word: {word} -> {number_map[word]}")
                return number_map[word]
        
        print("No number found in speech")
        tts.speak("Please say a number clearly")
    except Exception as e:
        print(f"Error: {e}")
        tts.speak("Please try again")
    
    return None

def get_yes_no_from_voice(recognizer, source, tts):
    """Get yes/no from voice input"""
    try:
        audio = recognizer.listen(source, timeout=7)
        text = recognizer.recognize_google(audio).lower()
        print(f"You said: {text}")
        return "yes" in text or "yeah" in text
    except Exception as e:
        print(f"Error: {e}")
        tts.speak("Please try again")
        return False

def get_game_settings_from_voice():
    """Get game settings through interactive voice dialog"""
    print("\nStarting game setup...")
    recognizer = sr.Recognizer()
    settings = {}
    tts = ChallengeTTS()
    
    # Define questions
    questions = [
        ("How many minutes per side?", "time_control", get_number_from_voice),
        ("Would you like this to be a rated game?", "rated", get_yes_no_from_voice),
        ("How many seconds increment?", "increment", get_number_from_voice),
        ("Is this an open challenge?", "is_open", get_yes_no_from_voice)
    ]
    
    with sr.Microphone() as source:
        try:
            # Adjust mic for ambient noise
            print("\nAdjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Noise adjustment complete")
            
            # Ask each question in sequence
            for question, setting_key, get_answer_func in questions:
                # Try up to 3 times for each question
                for attempt in range(3):
                    tts.speak(question)
                    answer = get_answer_func(recognizer, source, tts)
                    
                    if answer is not None:
                        settings[setting_key] = answer
                        break
                    
                    if attempt < 2:
                        tts.speak("Please try again")
                
                # Use defaults if all attempts fail
                if setting_key not in settings:
                    defaults = {"time_control": 5, "rated": False, "increment": 3, "is_open": True}
                    settings[setting_key] = defaults[setting_key]
                    tts.speak(f"Using default value for {setting_key}")
            
            # Handle opponent name if not open challenge
            if not settings.get('is_open', True):
                tts.speak("Please spell out the username of your opponent")
                try:
                    audio = recognizer.listen(source, timeout=10)
                    opponent = recognizer.recognize_google(audio).lower().replace(" ", "")
                    tts.speak(f"Challenging player: {opponent}")
                    settings['opponent'] = opponent
                except Exception as e:
                    print(f"Error getting opponent: {e}")
                    tts.speak("Could not understand opponent name. Using default from settings")
            
            print(f"Final settings: {settings}")
            return settings
            
        finally:
            tts.cleanup() 