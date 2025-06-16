"""Module for parsing game setup voice commands using Deepgram Speech Services"""
import os
import glob
import time
import pyaudio
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from dotenv import load_dotenv
from gtts import gTTS
import pygame

# Load environment variables
load_dotenv()

class DeepgramChallengeTTS:
    def __init__(self):
        # Clean up any leftover files from previous runs
        pygame.mixer.init()
        self.count = 0
        self.temp_files = []  # Track all created files
        self.temp_pattern = "temp_speech_"  # Base pattern for temp files
        self._cleanup_previous_files()
        
        # Initialize Deepgram Speech Service
        self.api_key = os.getenv('DEEPGRAM_API_KEY')
        
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
        
        # Initialize client (it will automatically use DEEPGRAM_API_KEY from environment)
        self.client = DeepgramClient()
        
        # Audio settings
        self.RATE = 16000
        self.CHUNK = 1024
        self.CHANNELS = 1
        self.FORMAT = pyaudio.paInt16
        
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
        
    def recognize_speech(self, timeout=7):
        """Capture audio with pyaudio, save as WAV file, then analyze with Deepgram"""
        print("\nListening...")
        
        try:
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            print("Recording...")
            frames = []
            
            # Record for specified duration
            for _ in range(0, int(self.RATE / self.CHUNK * timeout)):
                data = stream.read(self.CHUNK)
                frames.append(data)
            
            print("Finished recording.")
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save audio to temporary WAV file
            import tempfile
            import wave
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_filename = temp_audio.name
                
                # Write WAV file
                with wave.open(temp_filename, 'wb') as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(frames))
            
            # Read the audio file and send to Deepgram
            with open(temp_filename, "rb") as file:
                buffer_data = file.read()

            payload: FileSource = {
                "buffer": buffer_data,
            }
            
            # Configure Deepgram options
            options = PrerecordedOptions(
                model="nova-3",
                language="en-US",
                smart_format=True,
                punctuate=True,
            )
            
            # Send to Deepgram for transcription
            response = self.client.listen.rest.v("1").transcribe_file(payload, options)
            
            # Clean up temporary file
            os.unlink(temp_filename)
            
            # Extract transcription
            if response.results and response.results.channels:
                transcript = response.results.channels[0].alternatives[0].transcript
                if transcript.strip():
                    text = transcript.lower().strip()
                    print(f"You said: {text}")
                    return text
                else:
                    print("No speech detected")
                    return None
            else:
                print("No speech could be recognized")
                return None
                
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            # Try to clean up temp file if it exists
            try:
                if 'temp_filename' in locals():
                    os.unlink(temp_filename)
            except:
                pass
            return None

def get_number_from_voice(tts):
    """Get a number from voice input using Deepgram Speech"""
    print("\nListening for number...")
    
    try:
        text = tts.recognize_speech()
        if not text:
            return None
            
        # Try to extract number
        if '.' in text:
            text = text.replace('.', '')
        words = text.lower().split()
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

def get_yes_no_from_voice(tts):
    """Get yes/no from voice input using Deepgram Speech"""
    try:
        text = tts.recognize_speech()
        if not text:
            return False
            
        print(f"You said: {text}")
        return "yes" in text or "yeah" in text
    except Exception as e:
        print(f"Error: {e}")
        tts.speak("Please try again")
        return False

def get_game_settings_from_voice():
    """Get game settings through interactive voice dialog using Deepgram Speech"""
    print("\nStarting game setup with Deepgram Speech Services...")
    settings = {}
    tts = DeepgramChallengeTTS()
    
    # Define questions
    questions = [
        ("How many minutes per side?", "time_control", get_number_from_voice),
        ("Would you like this to be a rated game?", "rated", get_yes_no_from_voice),
        ("How many seconds increment?", "increment", get_number_from_voice),
        ("Is this an open challenge?", "is_open", get_yes_no_from_voice)
    ]
    
    try:
        # Ask each question in sequence
        for question, setting_key, get_answer_func in questions:
            # Try up to 3 times for each question
            for attempt in range(3):
                tts.speak(question)
                answer = get_answer_func(tts)
                
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
            tts.speak("Getting opponent name from environment variable")
            try:
                opponent = os.getenv('OPPONENT_NAME')
                if opponent:
                    opponent = opponent.replace(" ", "")
                    tts.speak(f"Challenging player: {opponent}")
                    settings['opponent'] = opponent
            except Exception as e:
                print(f"Error getting opponent: {e}")
                tts.speak("Could not understand opponent name. Using default from settings")
        
        print(f"Final settings: {settings}")
        return settings
        
    finally:
        tts.cleanup() 