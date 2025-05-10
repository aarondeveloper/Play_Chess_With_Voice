"""Module for parsing game setup voice commands"""
import speech_recognition as sr
import pyttsx3
import threading

def create_engine():
    """Create a new TTS engine in its own thread"""
    engine = pyttsx3.init()
    engine.startLoop(False)  # Start non-blocking
    return engine

def kill_engine(engine):
    """Clean up engine"""
    if engine:
        engine.endLoop()
        del engine

def speak_prompt(text, engine=None):
    """Speak a prompt to the user"""
    print(f"\nPrompt: {text}")  # Debug output
    try:
        if not engine:
            engine = create_engine()
            engine.say(text)
            engine.iterate()
            kill_engine(engine)
        else:
            engine.say(text)
            engine.iterate()
    except Exception as e:
        print(f"Speech error: {e}")

def get_number_from_voice(recognizer, source, engine=None, max_retries=3):
    """Get a number from voice input with retries"""
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
        speak_prompt("Please say a number clearly", engine)
    except Exception as e:
        print(f"Error: {e}")
        speak_prompt("Please try again", engine)
    
    return None

def get_yes_no_from_voice(recognizer, source):
    """Get yes/no from voice input"""
    try:
        audio = recognizer.listen(source, timeout=5)
        text = recognizer.recognize_google(audio).lower()
        print(f"You said: {text}")
        return "yes" in text or "yeah" in text
    except Exception as e:
        print(f"Error: {e}")
    return False

def create_recognizer():
    """Create a new speech recognizer in its own thread"""
    recognizer = sr.Recognizer()
    thread = threading.Thread(target=lambda: None, daemon=True)
    thread.start()
    return recognizer, thread

def kill_recognizer(recognizer, thread):
    """Clean up recognizer and its thread"""
    if thread and thread.is_alive():
        thread.join()
    if recognizer:
        del recognizer

def get_game_settings_from_voice():
    """Get game settings through interactive voice dialog"""
    print("\nStarting game setup...")
    recognizer, rec_thread = create_recognizer()
    settings = {}
    
    # Create engine
    setup_engine = create_engine()
    
    with sr.Microphone() as source:
        try:
            print("\nAdjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Noise adjustment complete")
            
            # Get time control
            print("\n=== Time Control Setup ===")
            for attempt in range(3):  # Try 3 times
                speak_prompt("How many minutes per side?", setup_engine)
                print("Waiting for time control input...")
                time_control = get_number_from_voice(recognizer, source, setup_engine)
                if time_control is not None:
                    break
                print("Trying again...")
            
            if time_control is None:
                print("Using default time control")
                speak_prompt("Could not understand time control. Using default 5 minutes", setup_engine)
                time_control = 5
            speak_prompt(f"You chose {time_control} minutes", setup_engine)
            settings['time_control'] = time_control
            
            # Get rated preference
            speak_prompt("Would you like this to be a rated game? Say yes or no", setup_engine)
            rated = get_yes_no_from_voice(recognizer, source)
            speak_prompt(f"You chose {'rated' if rated else 'unrated'}", setup_engine)
            settings['rated'] = rated
            
            # Get increment
            speak_prompt("How many seconds increment?", setup_engine)
            increment = get_number_from_voice(recognizer, source, setup_engine)
            if increment is None:
                speak_prompt("Could not understand increment. Using default 3 seconds", setup_engine)
                increment = 3
            speak_prompt(f"You chose {increment} seconds increment", setup_engine)
            settings['increment'] = increment
            
            # Get challenge type
            speak_prompt("Is this an open challenge? Say yes for open, no for specific player", setup_engine)
            is_open = get_yes_no_from_voice(recognizer, source)
            settings['is_open'] = is_open
            
            if not is_open:
                speak_prompt("Please spell out the username of your opponent", setup_engine)
                try:
                    audio = recognizer.listen(source, timeout=10)
                    opponent = recognizer.recognize_google(audio).lower().replace(" ", "")
                    speak_prompt(f"Challenging player: {opponent}", setup_engine)
                    settings['opponent'] = opponent
                except Exception as e:
                    print(f"Error getting opponent: {e}")
                    speak_prompt("Could not understand opponent name. Using default from settings", setup_engine)
            
            print(f"Final settings: {settings}")
            return settings
        finally:
            # Clean up both engine and recognizer
            kill_engine(setup_engine)
            kill_recognizer(recognizer, rec_thread)
    
    return None 