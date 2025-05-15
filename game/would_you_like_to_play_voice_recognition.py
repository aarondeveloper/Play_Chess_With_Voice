"""Module for asking if user wants to play"""
import speech_recognition as sr
import os
from game.create_challenge_voice_recognition import ChallengeTTS
import time
def ask_to_play(game_manager=None):
    """Ask if the user wants to play chess"""
    print("\n=== CHESS VOICE COMMAND CENTER ===")
    
    # Create TTS engine
    tts = ChallengeTTS()
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Ask question
            tts.speak("Would you like to play a game of chess?")
            print("\nSay 'yes' to play or 'no' to quit")
            
            try:
                # Listen for response
                audio = recognizer.listen(source, timeout=5)
                response = recognizer.recognize_google(audio).lower()
                print(f"You said: {response}")
                
                if "no" in response or "quit" in response or "exit" in response:
                    tts.speak("Goodbye!")
                    print("\nThanks for playing! Goodbye.")
                    return False
                elif "yes" in response or "yeah" in response:
                    return True
                else:
                    tts.speak("Please say yes or no clearly")
                    return None
            except Exception as e:
                print(f"Error: {e}")
                tts.speak("Please say yes or no clearly")
                return None
    
    finally:
        print("Voice recognition completed")
        time.sleep(5)
        tts.cleanup()
