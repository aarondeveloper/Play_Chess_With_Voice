"""
Module for getting puzzle settings through voice interaction using Deepgram Speech Services
"""
import os
from dotenv import load_dotenv
from .deepgram_challenge_voice_recognition import DeepgramChallengeTTS

# Load environment variables
load_dotenv()

def get_puzzle_difficulty_from_voice(tts):
    """Get puzzle difficulty from voice input"""
    print("\nListening for difficulty...")
    
    try:
        text = tts.recognize_speech()
        if not text:
            return "normal"
            
        text = text.lower().strip().rstrip('.')
        print(f"You said: {text}")
        
        # Map spoken words to difficulty levels
        difficulty_map = {
            'easiest': 'easiest',
            'easy': 'easiest', 
            'easier': 'easier',
            'normal': 'normal',
            'medium': 'normal',
            'hard': 'harder',
            'harder': 'harder',
            'hardest': 'hardest',
            'expert': 'hardest'
        }
        
        for word in text.split():
            if word in difficulty_map:
                difficulty = difficulty_map[word]
                print(f"Selected difficulty: {difficulty}")
                return difficulty
                
        print("Could not understand difficulty, using normal")
        return "normal"
        
    except Exception as e:
        print(f"Error: {e}")
        return "normal"

def get_puzzle_color_from_voice(tts):
    """Get puzzle color preference from voice input"""
    print("\nListening for color preference...")
    
    try:
        text = tts.recognize_speech()
        if not text:
            return None  # Random color
            
        text = text.lower().strip().rstrip('.')
        print(f"You said: {text}")
        
        if 'white' in text or 'play as white' in text:
            print("Selected color: white")
            return "white"
        elif 'black' in text or 'play as black' in text:
            print("Selected color: black")
            return "black"
        else:
            print("No color preference, will be random")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_puzzle_theme_from_voice(tts):
    """Get puzzle theme from voice input"""
    print("\nListening for theme preference...")
    
    try:
        text = tts.recognize_speech()
        if not text:
            return None  # No theme filter
            
        text = text.lower().strip().rstrip('.')
        print(f"You said: {text}")
        
        # Map spoken words to puzzle themes
        theme_map = {
            'endgame': 'endgame',
            'end game': 'endgame',
            'opening': 'opening',
            'middlegame': 'middlegame',
            'middle game': 'middlegame',
            'tactics': 'tactics',
            'tactic': 'tactics',
            'checkmate': 'checkmate',
            'mate': 'checkmate',
            'sacrifice': 'sacrifice',
            'sac': 'sacrifice',
            'fork': 'fork',
            'pin': 'pin',
            'skewer': 'skewer',
            'discovered': 'discovered attack',
            'discovered attack': 'discovered attack',
            'deflection': 'deflection',
            'attraction': 'attraction',
            'clearance': 'clearance',
            'interference': 'interference',
            'blocking': 'blocking',
            'x-ray': 'x-ray attack',
            'windmill': 'windmill',
            'underpromotion': 'underpromotion',
            'smothered': 'smothered mate',
            'back rank': 'back rank mate',
            'backrank': 'back rank mate'
        }
        
        for word in text.split():
            if word in theme_map:
                theme = theme_map[word]
                print(f"Selected theme: {theme}")
                return theme
                
        print("No specific theme recognized, will be random")
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_puzzle_settings_from_voice():
    """Get complete puzzle settings through voice interaction"""
    print("\n=== PUZZLE SETTINGS VOICE SETUP ===")
    
    tts = DeepgramChallengeTTS()
    settings = {}
    
    try:
        # Ask for difficulty
        tts.speak("What difficulty would you like? Say easiest, easier, normal, harder, or hardest")
        settings['difficulty'] = get_puzzle_difficulty_from_voice(tts)
        
        # Ask for color preference
        tts.speak("Do you want to play as white, black, or random?")
        settings['color'] = get_puzzle_color_from_voice(tts)
        
        # Ask for theme (optional)
        tts.speak("Do you have a specific theme in mind? Say endgame, tactics, checkmate, or skip")
        settings['theme'] = get_puzzle_theme_from_voice(tts)
        
        print(f"\nFinal puzzle settings: {settings}")
        return settings
        
    except Exception as e:
        print(f"Error in puzzle settings: {e}")
        # Return default settings
        return {
            'difficulty': 'normal',
            'color': None,
            'theme': None
        }
    finally:
        tts.cleanup()
