"""
Module for parsing chess SAN notation from spoken text.
Converts voice input to SAN format, then uses python-chess to convert to UCI.
"""
import re
import chess

def parse_voice_to_san(text):
    """Convert spoken chess moves to SAN format."""
    text = text.lower().strip()
    print(f"DEBUG SAN: Parsing voice text: '{text}'")
    
    # Clean punctuation from text
    words = text.split()
    cleaned_words = []
    
    for word in words:
        # Remove punctuation from each word
        cleaned_word = re.sub(r'[^\w]', '', word)
        if cleaned_word:  # Only add non-empty words
            cleaned_words.append(cleaned_word)
    
    print(f"DEBUG SAN: Cleaned words: {cleaned_words}")
    
    # Dictionary mapping spoken file names to chess notation
    files = {
        'a': 'a', 'alpha': 'a', 'ay': 'a', 'hey': 'a',
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
    
    # Piece name mappings
    pieces = {
        'king': 'K',
        'queen': 'Q',
        'rook': 'R',
        'bishop': 'B',
        'knight': 'N',
        'night': 'N',
        'pawn': '',  # Pawns don't have a letter in SAN,
        'pon': ''
    }
    
    # Handle castling first
    if any(word in cleaned_words for word in ["castle", "castles", "castling"]):
        is_queenside = any(word in cleaned_words for word in ["queen", "queenside", "long", "queens"])
        san_move = "O-O-O" if is_queenside else "O-O"
        print(f"DEBUG SAN: Parsed as castling: '{san_move}'")
        return san_move
    
    # Special handling for pawn captures with patterns like:
    # "pawn from h takes g5" or "h pawn takes g5"
    if "pawn" in cleaned_words and any(capture_word in cleaned_words for capture_word in ["takes", "captures", "x"]):
        print("DEBUG SAN: Detected pawn capture pattern")
        
        # Look for source file patterns
        pawn_index = cleaned_words.index("pawn")
        capture_index = -1
        for i, word in enumerate(cleaned_words):
            if word in ["takes", "captures", "x"]:
                capture_index = i
                break
        
        source_file = None
        
        # Pattern 1: "pawn from h takes g5"
        if "from" in cleaned_words:
            from_index = cleaned_words.index("from")
            if from_index + 1 < len(cleaned_words) and cleaned_words[from_index + 1] in files:
                source_file = files[cleaned_words[from_index + 1]]
                print(f"DEBUG SAN: Found pawn source file from 'from' pattern: {source_file}")
        
        # Pattern 2: "h pawn takes g5" - file letter before "pawn"
        elif pawn_index > 0 and cleaned_words[pawn_index - 1] in files:
            source_file = files[cleaned_words[pawn_index - 1]]
            print(f"DEBUG SAN: Found pawn source file before 'pawn': {source_file}")
        
        # Pattern 3: Look for a file letter anywhere before the capture word
        if not source_file and capture_index > 0:
            for i in range(capture_index):
                if cleaned_words[i] in files:
                    source_file = files[cleaned_words[i]]
                    print(f"DEBUG SAN: Found pawn source file before capture: {source_file}")
                    break
        
        # Find target square after capture word
        target_square = None
        if capture_index >= 0:
            for i in range(capture_index + 1, len(cleaned_words)):
                word = cleaned_words[i]
                # Look for file + rank combination
                if word in files and i + 1 < len(cleaned_words) and cleaned_words[i + 1] in ranks:
                    target_square = files[word] + ranks[cleaned_words[i + 1]]
                    print(f"DEBUG SAN: Found pawn target square: {target_square}")
                    break
                # Check for combined square like "g5"
                elif len(word) == 2 and word[0] in files and word[1] in ranks:
                    target_square = files[word[0]] + ranks[word[1]]
                    print(f"DEBUG SAN: Found pawn combined target square: {target_square}")
                    break
        
        # Check for promotion in pawn capture
        promotion = None
        if "promote" in cleaned_words or "promotes" in cleaned_words:
            promote_index = -1
            for i, word in enumerate(cleaned_words):
                if word in ["promote", "promotes"]:
                    promote_index = i
                    break
            
            if promote_index >= 0:
                # Look for the promotion piece after "promote", skipping "to" if present
                j = promote_index + 1
                while j < len(cleaned_words) and cleaned_words[j] == "to":
                    j += 1
                
                if j < len(cleaned_words) and cleaned_words[j] in ["queen", "rook", "bishop", "knight", "night"]:
                    promotion_map = {"queen": "Q", "rook": "R", "bishop": "B", "knight": "N", "night": "N"}
                    promotion = promotion_map[cleaned_words[j]]
                    print(f"DEBUG SAN: Found pawn capture promotion: {promotion}")
        
        # Build pawn capture SAN
        if source_file and target_square:
            san_move = source_file + "x" + target_square
            if promotion:
                san_move += "=" + promotion
            print(f"DEBUG SAN: Built pawn capture SAN: '{san_move}'")
            return san_move
        else:
            print(f"DEBUG SAN: Incomplete pawn capture - source_file: {source_file}, target_square: {target_square}")
    
    # Look for piece type (non-pawn pieces or non-capture pawn moves)
    piece_type = None
    capture = False
    target_square = None
    from_file = None
    from_rank = None
    promotion = None
    
    i = 0
    while i < len(cleaned_words):
        word = cleaned_words[i]
        
        # Check for piece names (but only if we haven't found a promotion piece)
        if word in pieces and piece_type is None:
            piece_type = pieces[word]
            print(f"DEBUG SAN: Found piece: {word} -> {piece_type}")
            i += 1
            continue
        
        # Check for capture indicators
        if word in ["takes", "captures", "x"]:
            capture = True
            print(f"DEBUG SAN: Found capture indicator")
            i += 1
            continue
        
        # Check for "to" (indicates destination)
        if word == "to":
            i += 1
            continue
        
        # Check for promotion
        if word == "promote" or word == "promotes":
            # Look for the promotion piece, skipping "to" if present
            j = i + 1
            while j < len(cleaned_words) and cleaned_words[j] == "to":
                j += 1
            
            if j < len(cleaned_words) and cleaned_words[j] in ["queen", "rook", "bishop", "knight", "night"]:
                promotion_map = {"queen": "Q", "rook": "R", "bishop": "B", "knight": "N", "night": "N"}
                promotion = promotion_map[cleaned_words[j]]
                print(f"DEBUG SAN: Found promotion: {promotion}")
                i = j + 1  # Skip to after the promotion piece
                continue
            else:
                i += 1
                continue
        
        # Check for disambiguation (from file/rank)
        if word == "from":
            if i + 1 < len(cleaned_words):
                next_word = cleaned_words[i + 1]
                if next_word in files:
                    from_file = files[next_word]
                    print(f"DEBUG SAN: Found from file: {from_file}")
                elif next_word in ranks:
                    from_rank = ranks[next_word]
                    print(f"DEBUG SAN: Found from rank: {from_rank}")
                i += 2
                continue
            i += 1
            continue
        
        # Check for target square
        # Look for file + rank combination
        if word in files:
            file_letter = files[word]
            # Look for rank in next word
            if i + 1 < len(cleaned_words) and cleaned_words[i + 1] in ranks:
                rank_number = ranks[cleaned_words[i + 1]]
                target_square = file_letter + rank_number
                print(f"DEBUG SAN: Found target square: {target_square}")
                i += 2
                continue
        
        # Check for combined square like "c5"
        if len(word) == 2 and word[0] in files and word[1] in ranks:
            file_letter = files[word[0]]
            rank_number = ranks[word[1]]
            target_square = file_letter + rank_number
            print(f"DEBUG SAN: Found combined target square: {target_square}")
            i += 1
            continue
        
        i += 1
    
    # Build SAN notation
    if not target_square:
        print("DEBUG SAN: No target square found")
        return None
    
    san_move = ""
    
    # Add piece (empty for pawns)
    if piece_type is not None:
        san_move += piece_type
    
    # Special handling for pawn captures: if it's a pawn capture but no from_file specified,
    # this is an error condition for captures
    if piece_type == '' and capture and not from_file:
        print("DEBUG SAN: ERROR - Pawn capture requires source file specification")
        return None
    
    # Add disambiguation
    if from_file:
        san_move += from_file
    if from_rank:
        san_move += from_rank
    
    # Add capture indicator
    if capture:
        san_move += "x"
    
    # Add target square
    san_move += target_square
    
    # Add promotion
    if promotion:
        san_move += "=" + promotion
    
    print(f"DEBUG SAN: Built SAN move: '{san_move}'")
    return san_move

def convert_san_to_uci(san_move, board_state):
    """Convert SAN notation to UCI using python-chess."""
    try:
        print(f"DEBUG SAN: Converting '{san_move}' to UCI with board position")
        
        # Parse the SAN move using python-chess
        move = board_state.parse_san(san_move)
        uci_move = move.uci()
        
        print(f"DEBUG SAN: Successfully converted '{san_move}' -> '{uci_move}'")
        return uci_move
        
    except chess.InvalidMoveError as e:
        print(f"DEBUG SAN: Invalid move '{san_move}': {e}")
        return None
    except chess.IllegalMoveError as e:
        print(f"DEBUG SAN: Illegal move '{san_move}': {e}")
        return None
    except Exception as e:
        print(f"DEBUG SAN: Error converting '{san_move}': {e}")
        return None

def parse_chess_notation_san_to_uci(text, board_state=None):
    """
    Main function: Convert spoken text to UCI via SAN.
    
    Args:
        text (str): Spoken chess move text
        board_state (chess.Board): Current board position (optional for testing)
        
    Returns:
        str or None: UCI move or None if parsing failed
    """
    print(f"DEBUG SAN: Starting parse for: '{text}'")
    
    # Use default starting position if no board provided
    if board_state is None:
        board_state = chess.Board()
        print("DEBUG SAN: Using default starting position for testing")
    
    # Handle special commands
    text_lower = text.lower().strip()
    if 'exit' in text_lower or 'quit' in text_lower:
        return "EXIT"
    if "resign" in text_lower:
        return "resign"
    if "accept draw" in text_lower:
        return "accept draw"
    if "decline draw" in text_lower:
        return "decline draw"
    if "draw" in text_lower:
        return "draw"
    
    # Convert voice to SAN
    san_move = parse_voice_to_san(text)
    if not san_move:
        print("DEBUG SAN: Failed to parse voice to SAN")
        return None
    
    # Convert SAN to UCI
    uci_move = convert_san_to_uci(san_move, board_state)
    if not uci_move:
        print("DEBUG SAN: Failed to convert SAN to UCI")
        return None
    
    print(f"DEBUG SAN: Final result: '{text}' -> '{san_move}' -> '{uci_move}'")
    return uci_move
