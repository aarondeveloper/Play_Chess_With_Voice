"""Module for asking if user wants to play using Deepgram Speech Services"""
import os
import time
from dotenv import load_dotenv
from game.deepgram_challenge_voice_recognition import DeepgramChallengeTTS

# Load environment variables
load_dotenv()

def ask_to_play(game_manager=None):
    """Ask if the user wants to play chess using Deepgram Speech Services"""
    print("\n=== CHESS VOICE COMMAND CENTER (Deepgram Speech) ===")
    
    # Create TTS engine
    tts = DeepgramChallengeTTS()
    
    try:
        # Ask question
        tts.speak("Would you like to play a game of chess?")
        print("\nSay 'yes' to play or 'no' to quit")
        
        try:
            # Listen for response using Deepgram Speech (shorter timeout)
            response = tts.recognize_speech(timeout=3)
            if not response:
                tts.speak("Please say yes or no clearly")
                return None
                
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
        time.sleep(2)
        tts.cleanup() 