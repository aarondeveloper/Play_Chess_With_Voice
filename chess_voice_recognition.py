"""
Main module for chess voice recognition functionality.
"""
import speech_recognition as sr
from chess_notation_parser import parse_chess_notation_for_lichess, get_promotion_piece

def recognize_speech(timeout=5, phrase_time_limit=5):
    """
    Listen for speech and convert it to text using Google Speech Recognition.
    
    Args:
        timeout (int): How long to wait for speech to start
        phrase_time_limit (int): Maximum length of speech to process
        
    Returns:
        str or None: Recognized text or None if recognition failed
    """
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("\nListening... Say a chess move now!")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("Processing...")
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None
    
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def process_chess_command(text):
    """
    Process a spoken chess command and convert it to a UCI move.
    
    Args:
        text (str): The spoken text to process
        
    Returns:
        str or None: UCI formatted move or None if parsing failed
    """
    if not text:
        return None
        
    # Check for exit command
    if 'exit' in text.lower() or 'quit' in text.lower():
        return "EXIT"
    
    # Try to parse the move
    move = parse_chess_notation_for_lichess(text)
    if move:
        print(f"Parsed as UCI move: {move}")
        print(f"This is the format needed for the Lichess API.")
        
        # Provide a more human-readable interpretation
        if move == "e1g1":
            print("Interpreted as: Castle kingside (white)")
        elif move == "e1c1":
            print("Interpreted as: Castle queenside (white)")
        elif move == "e8g8":
            print("Interpreted as: Castle kingside (black)")
        elif move == "e8c8":
            print("Interpreted as: Castle queenside (black)")
        elif len(move) == 4:
            print(f"Interpreted as: Move from {move[0:2]} to {move[2:4]}")
        elif len(move) == 5:  # Promotion
            print(f"Interpreted as: Move from {move[0:2]} to {move[2:4]} and promote to {get_promotion_piece(move[4])}")
    else:
        print("Could not parse this as a UCI chess move.")
        print("Try saying something like:")
        print("- 'e2 to e4'")
        print("- 'castle kingside'")
        print("- 'e7 to e8 promote to queen'")
    
    return move

def get_chess_move_from_voice():
    """
    Complete process to get a chess move from voice input.
    
    Returns:
        str or None: UCI formatted move or None if process failed
    """
    text = recognize_speech()
    return process_chess_command(text) 