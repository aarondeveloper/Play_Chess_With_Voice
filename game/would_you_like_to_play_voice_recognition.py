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
    #thread = threading.Thread(target=lambda: None, daemon=True)
    #thread.start()
    return recognizer

def kill_recognizer(recognizer):
    """Clean up recognizer and its thread"""
    #if thread and thread.is_alive():
    #    thread.join()
    if recognizer:
        del recognizer

def ask_to_play(game_manager):
    """Ask if user wants to play a game"""
    engine = create_engine()
    recognizer = create_recognizer()
    
    try:
        # Use our own engine instead of game_manager's
        engine.say("Would you like to play a game of chess?")
        engine.iterate()
        print("\nSay 'yes' to play or 'no' to quit")
        
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=5)
                response = recognizer.recognize_google(audio).lower()
                print(f"You said: {response}")
                
                if "no" in response or "quit" in response or "exit" in response:
                    engine.say("Goodbye!")
                    engine.iterate()
                    print("\nThanks for playing! Goodbye.")
                    return False
                elif "yes" in response or "yeah" in response:
                    return True
                else:
                    engine.say("Please say yes or no clearly")
                    engine.iterate()
                    return None
            except Exception as e:
                print(f"Error: {e}")
                engine.say("Please say yes or no clearly")
                engine.iterate()
                return None
    finally:
        kill_engine(engine)
        kill_recognizer(recognizer) 
        print("Engine and recognizer killed")