"""
Module for parsing chess notation from spoken text.
"""

def parse_chess_notation_for_lichess(text):
    """Convert spoken chess notation to UCI format for Lichess API."""
    text = text.lower().strip()
    print(f"DEBUG: Parsing text: '{text}'")
    
    # Dictionary mapping spoken file names to chess notation
    files = {
        'a': 'a', 'alpha': 'a', 'ay': 'a', '8': 'a', 'hey': 'a',
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
    
    # Split the text into words
    words = text.split()
    print(f"DEBUG: Words: {words}")
    
    # Find any two squares in the command
    squares = []
    
    for word in words:
        # Check for combined squares like "f5"
        if len(word) == 2 and word[0] in files and word[1] in ranks:
            squares.append((word[0], word[1]))
            continue
            
        # Check for separated squares like "f" and "5"
        if word in files:
            next_idx = words.index(word) + 1
            if next_idx < len(words) and words[next_idx] in ranks:
                squares.append((word, words[next_idx]))
    
    # If we found two squares, create the UCI move
    if len(squares) >= 2:
        from_square = squares[0]
        to_square = squares[1]
        move = f"{from_square[0]}{from_square[1]}{to_square[0]}{to_square[1]}"
        print(f"DEBUG: Found squares {squares}, making move {move}")
        return move
    
    # Handle castling separately
    if "castle" in words or "castles" in words or "castling" in words:
        is_queenside = any(word in words for word in ["queen", "queenside", "long", "queens"])
        move = "e1c1" if is_queenside else "e1g1"
        print(f"DEBUG: Parsed as '{move}' using pattern 'castle'")
        return move
    
    # If we couldn't parse a complete UCI move, return None
    print("DEBUG: Failed to parse move")
    return None

def get_promotion_piece(code):
    """Convert promotion code to full name."""
    pieces = {
        'q': 'Queen',
        'n': 'Knight',
        'b': 'Bishop',
        'r': 'Rook'
    }
    return pieces.get(code, code) 