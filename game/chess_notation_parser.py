"""
Module for parsing chess notation from spoken text.
"""
import re

def parse_chess_notation_for_lichess(text):
    """Convert spoken chess notation to UCI format for Lichess API."""
    text = text.lower().strip()
    print(f"DEBUG: Parsing text: '{text}'")
    
    # Check for promotion keywords
    promotion_piece = None
    if "promote" in text:
        if "queen" in text:
            promotion_piece = "q"
        elif "knight" in text:
            promotion_piece = "n"
        elif "bishop" in text:
            promotion_piece = "b"
        elif "rook" in text:
            promotion_piece = "r"
    
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
    
    # Dictionary for ranks (numbers) - expanded for Deepgram word output
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
    
    # Clean punctuation from text and split into words
    words = text.split()
    cleaned_words = []
    
    for word in words:
        # Remove punctuation from each word
        cleaned_word = re.sub(r'[^\w]', '', word)
        if cleaned_word:  # Only add non-empty words
            cleaned_words.append(cleaned_word)
    
    print(f"DEBUG: Original words: {words}")
    print(f"DEBUG: Cleaned words: {cleaned_words}")
    
    # Find any two squares in the command
    squares = []
    
    i = 0
    while i < len(cleaned_words):
        word = cleaned_words[i]
        
        # Check for combined squares like "f5"
        if len(word) == 2 and word[0] in files and word[1] in ranks:
            file_letter = files[word[0]]
            rank_number = ranks[word[1]]
            squares.append((file_letter, rank_number))
            i += 1
            continue
            
        # Check for separated squares like "f" and "5" or "e" and "two"
        if word in files:
            file_letter = files[word]
            # Look for the rank in the next word
            if i + 1 < len(cleaned_words):
                next_word = cleaned_words[i + 1]
                if next_word in ranks:
                    rank_number = ranks[next_word]
                    squares.append((file_letter, rank_number))
                    i += 2  # Skip both words since we used them
                    continue
        
        i += 1
    
    print(f"DEBUG: Found squares: {squares}")
    
    # If we found two squares, create the UCI move
    if len(squares) >= 2:
        from_square = squares[0]
        to_square = squares[1]
        move = f"{from_square[0]}{from_square[1]}{to_square[0]}{to_square[1]}"
        
        # Add promotion piece if specified
        if promotion_piece and to_square[1] in ['1', '8']:
            move += promotion_piece
            
        print(f"DEBUG: Found squares {squares}, making move {move}")
        return move
    
    # Handle castling separately
    if any(word in cleaned_words for word in ["castle", "castles", "castling"]):
        is_queenside = any(word in cleaned_words for word in ["queen", "queenside", "long", "queens"])
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