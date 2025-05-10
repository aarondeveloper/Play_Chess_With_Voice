"""Module for initial game play prompt"""
import speech_recognition as sr

def ask_to_play(game_manager):
    """Ask if user wants to play a game"""
    game_manager.speak_status("Would you like to play a game of chess?")
    print("\nSay 'yes' to play or 'no' to quit")
    
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
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