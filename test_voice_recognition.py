import speech_recognition as sr

def test_voice_recognition():
    recognizer = sr.Recognizer()
    
    print("Testing voice recognition...")
    print("Please say a chess move when prompted (e.g., 'e2 to e4' or 'Knight to f3')")
    
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("\nSay a chess move now!")
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        
        # Try to parse the move
        move = parse_chess_notation(text)
        if move:
            print(f"Parsed as UCI move: {move}")
        else:
            print("Could not parse this as a chess move. Try saying something like 'e2 to e4'")
        
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    
    return None

def parse_chess_notation(text):
    """Convert spoken chess notation to UCI format without board validation"""
    text = text.lower().strip()
    
    # Dictionary mapping spoken file names to chess notation
    files = {
        'a': 'a', 'alpha': 'a', 'ay': 'a',
        'b': 'b', 'bravo': 'b', 'bee': 'b',
        'c': 'c', 'charlie': 'c', 'see': 'c',
        'd': 'd', 'delta': 'd', 'dee': 'd',
        'e': 'e', 'echo': 'e', 'ee': 'e',
        'f': 'f', 'foxtrot': 'f', 'ef': 'f',
        'g': 'g', 'golf': 'g', 'gee': 'g',
        'h': 'h', 'hotel': 'h', 'aitch': 'h'
    }
    
    # Pattern: "e2 to e4" (explicit from-to)
    words = text.split()
    for i, word in enumerate(words):
        if i+2 < len(words) and word in files.values() and words[i+1].isdigit() and words[i+2] == "to":
            from_file = word
            from_rank = words[i+1]
            if i+4 < len(words) and words[i+3] in files.values() and words[i+4].isdigit():
                to_file = words[i+3]
                to_rank = words[i+4]
                move = from_file + from_rank + to_file + to_rank
                return move
    
    # Pattern: "knight f3" or "knight to f3" (piece to square)
    piece_names = {
        'pawn': 'p', 'knight': 'n', 'bishop': 'b', 
        'rook': 'r', 'queen': 'q', 'king': 'k'
    }
    
    for i, word in enumerate(words):
        if word in piece_names:
            piece = piece_names[word]
            # Look for destination square
            for j in range(i+1, len(words)):
                if j < len(words) and words[j] in files.values():
                    if j+1 < len(words) and words[j+1].isdigit():
                        to_file = words[j]
                        to_rank = words[j+1]
                        # We can't determine the exact move without a board
                        # But we can return the piece and destination
                        return f"{piece}:{to_file}{to_rank}"
    
    # If we couldn't parse the move
    return None

def continuous_test():
    """Run the voice recognition test in a loop"""
    print("Continuous voice recognition test. Say 'exit' or 'quit' to stop.")
    
    while True:
        text = test_voice_recognition()
        if text and ('exit' in text.lower() or 'quit' in text.lower()):
            print("Exiting voice recognition test.")
            break
        
        print("\nReady for another test? Say a move or 'exit' to quit.")

if __name__ == "__main__":
    # Ask if user wants single test or continuous testing
    print("Voice Recognition Test")
    print("1. Single test")
    print("2. Continuous testing")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "2":
        continuous_test()
    else:
        test_voice_recognition() 