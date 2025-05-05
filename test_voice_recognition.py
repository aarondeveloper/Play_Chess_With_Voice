import speech_recognition as sr

def test_voice_recognition():
    recognizer = sr.Recognizer()
    
    print("Testing voice recognition...")
    print("Please say a chess move when prompted (e.g., 'e2 to e4', 'Knight F3', 'Queen takes D6')")
    
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
            print(f"Parsed as: {move}")
            
            # Provide a more human-readable interpretation
            if 'x' in move:
                # Handle captures
                piece = move[0]
                dest = move[2:]  # Skip the 'x'
                print(f"Interpreted as: {get_piece_name(piece)} captures on {dest}")
            elif len(move) == 4 and move[0].isalpha() and move[1].isdigit():
                # Handle pawn moves like e2e4
                print(f"Interpreted as: Move from {move[0:2]} to {move[2:4]}")
            else:
                # Handle piece moves like Nf3
                piece = move[0]
                dest = move[1:]
                print(f"Interpreted as: {get_piece_name(piece)} to {dest}")
        else:
            print("Could not parse this as a chess move.")
            print("Try saying something like:")
            print("- 'e2 to e4'")
            print("- 'Knight F3'")
            print("- 'Bishop to C4'")
            print("- 'Queen takes D6'")
        
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
        'a': 'a', 'alpha': 'a', 'ay': 'a', '8': 'a',
        'b': 'b', 'bravo': 'b', 'bee': 'b', 'be': 'b',
        'c': 'c', 'charlie': 'c', 'see': 'c', 'sea': 'c',
        'd': 'd', 'delta': 'd', 'dee': 'd',
        'e': 'e', 'echo': 'e', 'ee': 'e',
        'f': 'f', 'foxtrot': 'f', 'ef': 'f',
        'g': 'g', 'golf': 'g', 'gee': 'g',
        'h': 'h', 'hotel': 'h', 'aitch': 'h'
    }
    
    # Dictionary for ranks (numbers)
    ranks = {
        'one': '1', '1': '1', 'won': '1',
        'two': '2', '2': '2', 'to': '2', 'too': '2',
        'three': '3', '3': '3', 'tree': '3',
        'four': '4', '4': '4', 'for': '4',
        'five': '5', '5': '5',
        'six': '6', '6': '6',
        'seven': '7', '7': '7',
        'eight': '8', '8': '8', 'ate': '8'
    }
    
    # Piece names mapping
    piece_names = {
        'pawn': 'p', 'p': 'p', 'pond': 'p',
        'knight': 'n', 'n': 'n', 'night': 'n', 'horse': 'n', 'knights': 'n',
        'bishop': 'b', 'b': 'b', 'shop': 'b',
        'rook': 'r', 'r': 'r', 'rock': 'r', 'brooke': 'r',
        'queen': 'q', 'q': 'q',
        'king': 'k', 'k': 'k'
    }
    
    # Capture words
    capture_words = ['takes', 'take', 'captures', 'capture', 'x', 'takes']
    
    # Split the text into words
    words = text.split()
    
    # Pattern: "Queen takes D6" (piece takes square)
    # This pattern needs to be checked first
    for i, word in enumerate(words):
        if word in piece_names:
            piece = piece_names[word]
            
            # Look for "takes" followed by destination
            for j in range(i+1, min(i+5, len(words))):
                if j < len(words) and words[j] in capture_words:
                    
                    # Look for destination after "takes"
                    # Case 1: Next word is like "D6" (combined file and rank)
                    if j+1 < len(words) and len(words[j+1]) == 2:
                        dest = words[j+1].lower()
                        file_char = dest[0]
                        rank_char = dest[1]
                        
                        if file_char in files and rank_char in ranks:
                            to_file = files[file_char]
                            to_rank = ranks[rank_char]
                            return f"{piece}x{to_file}{to_rank}"
                    
                    # Case 2: Next two words are like "D 6" (separate file and rank)
                    if j+2 < len(words):
                        file_word = words[j+1].lower()
                        rank_word = words[j+2].lower()
                        
                        if file_word in files and rank_word in ranks:
                            to_file = files[file_word]
                            to_rank = ranks[rank_word]
                            return f"{piece}x{to_file}{to_rank}"
    
    # Pattern: "e2 to e4" (explicit from-to)
    for i, word in enumerate(words):
        if i+2 < len(words) and word in files and words[i+1] in ranks and words[i+2] == "to":
            from_file = files[word]
            from_rank = ranks[words[i+1]]
            if i+4 < len(words) and words[i+3] in files and words[i+4] in ranks:
                to_file = files[words[i+3]]
                to_rank = ranks[words[i+4]]
                move = from_file + from_rank + to_file + to_rank
                return move
    
    # Special case for "Knight F3" pattern
    if len(words) == 2 and words[0] in piece_names:
        piece = piece_names[words[0]]
        # Check if second word contains both file and rank (like "F3")
        second_word = words[1]
        if len(second_word) == 2:
            file_char = second_word[0].lower()
            rank_char = second_word[1]
            if file_char in files and rank_char in ranks:
                to_file = files[file_char]
                to_rank = ranks[rank_char]
                return f"{piece}{to_file}{to_rank}"
    
    # Pattern: "knight f3" (piece and destination, no "to")
    for i, word in enumerate(words):
        if word in piece_names:
            piece = piece_names[word]
            # Look for destination square immediately after piece name
            if i+2 < len(words) and words[i+1] in files and words[i+2] in ranks:
                to_file = files[words[i+1]]
                to_rank = ranks[words[i+2]]
                return f"{piece}{to_file}{to_rank}"
            
            # Look for destination square with words between (e.g., "knight to f3")
            for j in range(i+1, min(i+5, len(words))):
                if j < len(words) and words[j] in files:
                    if j+1 < len(words) and words[j+1] in ranks:
                        to_file = files[words[j]]
                        to_rank = ranks[words[j+1]]
                        return f"{piece}{to_file}{to_rank}"
    
    # If we couldn't parse the move
    return None

def get_piece_name(piece_code):
    """Convert piece code to full name"""
    pieces = {
        'p': 'Pawn',
        'n': 'Knight',
        'b': 'Bishop',
        'r': 'Rook',
        'q': 'Queen',
        'k': 'King'
    }
    return pieces.get(piece_code, piece_code)

def continuous_test():
    """Run the voice recognition test in a loop with better timing"""
    recognizer = sr.Recognizer()
    
    print("Continuous voice recognition test.")
    print("Say a chess move when ready, or 'exit' or 'quit' to stop.")
    print("Press Enter when you're ready to start listening...")
    
    while True:
        # Wait for user to press Enter before starting to listen
        input("Press Enter when you're ready to say a move...")
        
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("\nListening... Say a chess move now!")
            try:
                # Listen with a longer timeout and phrase_time_limit
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("Processing...")
            except sr.WaitTimeoutError:
                print("No speech detected. Let's try again.")
                continue
        
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            
            if 'exit' in text.lower() or 'quit' in text.lower():
                print("Exiting voice recognition test.")
                break
            
            # Try to parse the move
            move = parse_chess_notation(text)
            if move:
                print(f"Parsed as: {move}")
                
                # Provide a more human-readable interpretation
                if 'x' in move:
                    # Handle captures
                    piece = move[0]
                    dest = move[2:]  # Skip the 'x'
                    print(f"Interpreted as: {get_piece_name(piece)} captures on {dest}")
                elif len(move) == 4 and move[0].isalpha() and move[1].isdigit():
                    # Handle pawn moves like e2e4
                    print(f"Interpreted as: Move from {move[0:2]} to {move[2:4]}")
                else:
                    # Handle piece moves like Nf3
                    piece = move[0]
                    dest = move[1:]
                    print(f"Interpreted as: {get_piece_name(piece)} to {dest}")
            else:
                print("Could not parse this as a chess move.")
                print("Try saying something like:")
                print("- 'e2 to e4'")
                print("- 'Knight F3'")
                print("- 'Bishop to C4'")
                print("- 'Queen takes D6'")
            
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        
        print("\n" + "-"*50)

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