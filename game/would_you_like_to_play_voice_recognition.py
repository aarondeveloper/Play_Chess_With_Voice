"""Module for initial game play prompt"""
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

def ask_to_play(game_manager):
    """Ask if user wants to play a game"""
    engine = create_engine()
    recognizer, rec_thread = create_recognizer()
    
    try:
        game_manager.speak_status("Would you like to play a game of chess?")
        print("\nSay 'yes' to play or 'no' to quit")
        
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=5)
                response = recognizer.recognize_google(audio).lower()
                print(f"You said: {response}")
                
                if "no" in response or "quit" in response or "exit" in response:
                    game_manager.speak_status("Goodbye!")
                    print("\nThanks for playing! Goodbye.")
                    return False
                elif "yes" in response or "yeah" in response:
                    return True
                else:
                    game_manager.speak_status("Please say yes or no clearly")
                    return None
            except Exception as e:
                print(f"Error: {e}")
                game_manager.speak_status("Please say yes or no clearly")
                return None
    finally:
        kill_engine(engine)
        kill_recognizer(recognizer, rec_thread) 