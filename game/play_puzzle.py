"""
Module for playing chess puzzles with voice interaction.
Enhanced with theme cycling to prevent puzzle caching.
"""
import chess
import chess.pgn
import io
import random
import webbrowser
import tempfile
import os
from .deepgram_voice_recognition import get_chess_move_from_voice, DeepgramVoiceRecognizer
from .deepgram_challenge_voice_recognition import DeepgramChallengeTTS
from .chess_notation_parser_SAN import parse_chess_notation_san_to_uci

class PuzzlePlayer:
    def __init__(self):
        """Initialize the puzzle player with TTS and theme cycling"""
        self.tts = DeepgramChallengeTTS()
        self.board = None
        self.solution_moves = []
        self.current_move_index = 0
        
        # Debug settings
        self.debug_mode = True  # Set to True for demo mode
        self.is_first_puzzle = True
        
        # Theme cycling to prevent caching - 100 unique themes
        # Core themes that are known to work with Lichess API
        core_themes = [
            "endgame", "tactics", "opening", "middlegame", "crushing", "short",
            "advancedPawn", "attackingF2F7", "backRank", "basicCheckmate",
            "bishopEndgame", "capture", "defensiveMove", "discoveredAttack",
            "doubleBishopEndgame", "enPassant", "exposedKing", "fork",
            "hangingPiece", "interference", "knightEndgame", "long",
            "mate", "mateIn1", "mateIn2", "mateIn3", "mateIn4", "mateIn5",
            "oneMove", "pawnEndgame", "pin", "promotion",
            "queenEndgame", "queenRookEndgame", "queensideAttack", "quietMove",
            "rookEndgame", "sacrifice", "skewer", "smotheredMate",
            "trappedPiece", "underPromotion", "veryLong", "xRayAttack",
            "zugzwang"
        ]
        
        # Create 100 unique themes by cycling through core themes with variations
        self.theme_cycle = []
        for i in range(100):
            base_theme = core_themes[i % len(core_themes)]
            if i < len(core_themes):
                self.theme_cycle.append(base_theme)
            else:
                # Add variations to create more unique themes
                variation = (i // len(core_themes)) + 1
                self.theme_cycle.append(f"{base_theme}_{variation}")
        self.current_theme_index = 0
    
    def get_next_theme(self):
        """Get the next theme in the cycle to prevent caching"""
        # Demo mode: skip theme for first puzzle
        if self.debug_mode and self.is_first_puzzle:
            print("🎯 Demo mode: Using default settings for first puzzle")
            self.is_first_puzzle = False
            return None
        
        theme = self.theme_cycle[self.current_theme_index]
        self.current_theme_index = (self.current_theme_index + 1) % len(self.theme_cycle)
        print(f"🎯 Using theme: {theme} (index: {self.current_theme_index - 1})")
        return theme
    
    def get_theme_stats(self):
        """Get statistics about theme usage"""
        return {
            "total_themes": len(self.theme_cycle),
            "current_index": self.current_theme_index,
            "themes_used": self.current_theme_index,
            "themes_remaining": len(self.theme_cycle) - self.current_theme_index
        }
        
    def setup_puzzle(self, puzzle_data):
        """Set up the puzzle board and solution"""
        print("🔧 Setting up puzzle...")
        
        if not puzzle_data:
            print("❌ No puzzle data provided")
            return False
            
        # Create a new board
        self.board = chess.Board()
        print("✅ Created new chess board")
        
        # Get the PGN from the game
        pgn = puzzle_data.get('game', {}).get('pgn', '')
        if not pgn:
            print("❌ No PGN found in puzzle data")
            print(f"Puzzle data keys: {list(puzzle_data.keys())}")
            if 'game' in puzzle_data:
                print(f"Game keys: {list(puzzle_data['game'].keys())}")
            return False
            
        print(f"✅ Found PGN: {pgn[:100]}...")
        
        # Parse the PGN to get all moves
        try:
            pgn_io = io.StringIO(pgn)
            game = chess.pgn.read_game(pgn_io)
            
            if not game:
                print("❌ Could not parse PGN")
                return False
                
            print("✅ Successfully parsed PGN")
            
            # Play all moves up to the puzzle position
            board = game.board()
            move_count = 0
            for move in game.mainline_moves():
                board.push(move)
                move_count += 1
                
            print(f"✅ Played {move_count} moves to reach puzzle position")
            
            # Set our board to the puzzle position
            self.board = board
            
            # Get the solution moves
            self.solution_moves = puzzle_data.get('puzzle', {}).get('solution', [])
            self.current_move_index = 0
            
            print(f"✅ Puzzle setup complete!")
            print(f"Solution moves: {self.solution_moves}")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up puzzle: {e}")
            return False
        
    def describe_board_position(self):
        """Describe the current board position to the user"""
        if not self.board:
            return
            
        # Create a dictionary to hold the locations of each piece
        pieces_on_board = {
            chess.WHITE: {
                chess.PAWN: [],
                chess.KNIGHT: [],
                chess.BISHOP: [],
                chess.ROOK: [],
                chess.QUEEN: [],
                chess.KING: [],
            },
            chess.BLACK: {
                chess.PAWN: [],
                chess.BISHOP: [],
                chess.KNIGHT: [],
                chess.ROOK: [],
                chess.QUEEN: [],
                chess.KING: [],
            },
        }

        # Iterate through all squares to find pieces
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                # Get the name of the square, e.g., "a1"
                square_name = chess.square_name(square)
                
                # Add the square name to the correct piece type and color list
                pieces_on_board[piece.color][piece.piece_type].append(square_name)

        # Describe the position with natural pauses
        description_parts = []
        
        # Determine whose turn it is
        turn_color = "White" if self.board.turn == chess.WHITE else "Black"
        description_parts.append(f"It is {turn_color}'s turn to move.")
        
        # Describe White pieces with natural formatting
        description_parts.append("White pieces:")
        for piece_type, locations in pieces_on_board[chess.WHITE].items():
            piece_name = chess.piece_name(piece_type).capitalize()
            if locations:
                # Format locations with commas and "and" for the last one
                if len(locations) == 1:
                    locations_text = f"{piece_name} on {locations[0]}"
                elif len(locations) == 2:
                    locations_text = f"{piece_name} on {locations[0]} and {locations[1]}"
                else:
                    locations_text = f"{piece_name} on {', '.join(locations[:-1])} and {locations[-1]}"
                description_parts.append(locations_text)
                
        # Describe Black pieces with natural formatting
        description_parts.append("Black pieces:")
        for piece_type, locations in pieces_on_board[chess.BLACK].items():
            piece_name = chess.piece_name(piece_type).capitalize()
            if locations:
                # Format locations with commas and "and" for the last one
                if len(locations) == 1:
                    locations_text = f"{piece_name} on {locations[0]}"
                elif len(locations) == 2:
                    locations_text = f"{piece_name} on {locations[0]} and {locations[1]}"
                else:
                    locations_text = f"{piece_name} on {', '.join(locations[:-1])} and {locations[-1]}"
                description_parts.append(locations_text)
        
        # Print the full description for debugging
        print(f"Board position: {' '.join(description_parts)}")
        
        # Just print the description (no voice - display_piece_locations handles voice)
        print("📋 Board position description:")
        for part in description_parts:
            print(f"  {part}")
        
        self.tts.speak("Take your time to think. What is your move?")
        self.tts.speak("At any point you can say 'exit puzzle' to quit")
    
    def display_piece_locations(self):
        """Display all piece locations in a web browser popup"""
        if not self.board:
            return
            
        # Determine whose turn it is
        turn_color = "White" if self.board.turn == chess.WHITE else "Black"
        
        # Build HTML content directly by scanning the board
        print("🔍 Building HTML content...")
        
        # Start HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Chess Position - Piece Locations</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ text-align: center; color: #333; margin-bottom: 10px; }}
                .turn {{ text-align: center; font-size: 18px; font-weight: bold; color: #666; margin-bottom: 30px; }}
                .pieces-container {{ display: flex; gap: 20px; }}
                .pieces-column {{ flex: 1; background: #f9f9f9; padding: 15px; border-radius: 8px; }}
                .pieces-column h3 {{ margin-top: 0; text-align: center; color: #333; }}
                .piece {{ margin: 8px 0; padding: 5px; background: white; border-radius: 4px; font-family: monospace; }}
                .white-column {{ border-left: 4px solid #ddd; }}
                .black-column {{ border-left: 4px solid #333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📋 CHESS POSITION - PIECE LOCATIONS</h1>
                <div class="turn">🎯 It is {turn_color}'s turn to move</div>
                
                <div class="pieces-container">
                    <div class="pieces-column white-column">
                        <h3>⚪ WHITE PIECES</h3>
        """
        
        # Collect white pieces by type
        white_pieces_by_type = {
            'King': [], 'Queen': [], 'Rook': [], 'Bishop': [], 'Knight': [], 'Pawn': []
        }
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                square_name = chess.square_name(square)
                piece_name = chess.piece_name(piece.piece_type).capitalize()
                white_pieces_by_type[piece_name].append(square_name)
        
        # Add white pieces to HTML in proper order
        for piece_type in ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']:
            if white_pieces_by_type[piece_type]:
                for square in white_pieces_by_type[piece_type]:
                    html_content += f'<div class="piece">{piece_type}: {square}</div>'
        
        html_content += """
                    </div>
                    <div class="pieces-column black-column">
                        <h3>⚫ BLACK PIECES</h3>
        """
        
        # Collect black pieces by type
        black_pieces_by_type = {
            'King': [], 'Queen': [], 'Rook': [], 'Bishop': [], 'Knight': [], 'Pawn': []
        }
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.BLACK:
                square_name = chess.square_name(square)
                piece_name = chess.piece_name(piece.piece_type).capitalize()
                black_pieces_by_type[piece_name].append(square_name)
        
        # Add black pieces to HTML in proper order
        for piece_type in ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']:
            if black_pieces_by_type[piece_type]:
                for square in black_pieces_by_type[piece_type]:
                    html_content += f'<div class="piece">{piece_type}: {square}</div>'
        
        html_content += """
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Count total pieces
        white_count = sum(len(pieces) for pieces in white_pieces_by_type.values())
        black_count = sum(len(pieces) for pieces in black_pieces_by_type.values())
        print(f"✅ Found {white_count} white pieces and {black_count} black pieces")
        
        # Print organized terminal output
        print("\n📋 CHESS POSITION - PIECE LOCATIONS")
        print(f"🎯 It is {turn_color}'s turn to move")
        print("\n⚪ WHITE PIECES:")
        for piece_type in ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']:
            if white_pieces_by_type[piece_type]:
                squares = ', '.join(white_pieces_by_type[piece_type])
                print(f"  {piece_type}: {squares}")
        
        print("\n⚫ BLACK PIECES:")
        for piece_type in ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']:
            if black_pieces_by_type[piece_type]:
                squares = ', '.join(black_pieces_by_type[piece_type])
                print(f"  {piece_type}: {squares}")
        
        # Voice output - just a simple summary (no blocking)
        self.tts.speak("Chess position loaded. You can see the piece locations in your browser.")
        
        # Use a fixed HTML file that gets updated
        html_file = os.path.join(tempfile.gettempdir(), 'chess_position.html')
        
        # Write/update the HTML file
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"📄 HTML file created at: {html_file}")
        
        # Open in browser (only if it's the first time)
        if not hasattr(self, '_browser_opened'):
            try:
                # Try different approaches to open the browser
                file_url = f'file://{html_file}'
                print(f"🌐 Attempting to open: {file_url}")
                
                # Try opening with webbrowser
                webbrowser.open(file_url)
                
                # Also try opening the file directly
                webbrowser.open(html_file)
                
                self._browser_opened = True
                print("🌐 Opened chess position in browser")
            except Exception as e:
                print(f"❌ Could not open browser: {e}")
                print(f"📄 You can manually open the file at: {html_file}")
        else:
            print("🔄 Updated chess position in browser")
            print(f"📄 File updated at: {html_file}")
        
        # Now read out all the pieces (after browser opens)
        self.tts.speak("Here are the piece locations on the board.")
        self.tts.speak(f"It is {turn_color}'s turn to move.")
        
        # Always start with the player who is to move
        if self.board.turn == chess.WHITE:
            self.tts.speak("White pieces:")
            for piece_type in ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']:
                if white_pieces_by_type[piece_type]:
                    squares = ', '.join(white_pieces_by_type[piece_type])
                    self.tts.speak(f"{piece_type} at {squares}")
            
            self.tts.speak("Black pieces:")
            for piece_type in ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']:
                if black_pieces_by_type[piece_type]:
                    squares = ', '.join(black_pieces_by_type[piece_type])
                    self.tts.speak(f"{piece_type} at {squares}")
        else:
            self.tts.speak("Black pieces:")
            for piece_type in ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']:
                if black_pieces_by_type[piece_type]:
                    squares = ', '.join(black_pieces_by_type[piece_type])
                    self.tts.speak(f"{piece_type} at {squares}")
            
            self.tts.speak("White pieces:")
            for piece_type in ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']:
                if white_pieces_by_type[piece_type]:
                    squares = ', '.join(white_pieces_by_type[piece_type])
                    self.tts.speak(f"{piece_type} at {squares}")
    
    def cleanup_html_file(self):
        """Clean up the HTML file when puzzle is finished"""
        try:
            html_file = os.path.join(tempfile.gettempdir(), 'chess_position.html')
            if os.path.exists(html_file):
                os.unlink(html_file)
                print("🗑️ Cleaned up chess position file")
        except:
            pass
        
    def get_user_move(self):
        """Get a move from the user via voice"""
        print("\n🎤 Listening for your move...")
        print("Say your move or 'exit puzzle' to quit")
        
        # Get move from voice (now with 60 second timeout)
        move_uci = get_chess_move_from_voice(self.board)
        
        if not move_uci:
            #self.tts.speak("I didn't catch that. Please speak clearly and try again.")
            return None
            
        # Check for exit command
        if "exit" in move_uci.lower():
            print("Exiting puzzle...")
            self.tts.speak("Exiting puzzle mode.")
            return "exit"
            
        # Convert UCI to chess.Move object
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                return move
            else:
                self.tts.speak("That is not a legal move. Please try again.")
                return None
        except ValueError:
            self.tts.speak("Invalid move format. Please try again.")
            return None
            
    def check_solution(self, user_move):
        """Check if the user's move matches the solution"""
        if self.current_move_index >= len(self.solution_moves):
            return False
            
        expected_move_uci = self.solution_moves[self.current_move_index]
        user_move_uci = user_move.uci()
        
        return user_move_uci == expected_move_uci
        
    def play_puzzle(self, puzzle_data):
        """Main function to play a puzzle"""
        print("\n=== CHESS PUZZLE SOLVER ===")
        
        # Setup the puzzle
        if not self.setup_puzzle(puzzle_data):
            print("❌ Failed to setup puzzle")
            return False
            
        # Display piece locations for demo
        self.display_piece_locations()
        
        # Describe the initial position
        self.describe_board_position()
        
        # Play through the solution moves
        while self.current_move_index < len(self.solution_moves):
            print(f"\n--- Move {self.current_move_index + 1} of {len(self.solution_moves)} ---")
            
            # Get user's move
            user_move = self.get_user_move()
            if not user_move:
                continue
                
            # Check if user wants to exit
            if user_move == "exit":
                return False
                
            # Check if it's correct
            if self.check_solution(user_move):
                print("✅ Correct move!")
                self.tts.speak("Correct!")
                
                # Make the user's move on the board
                self.board.push(user_move)
                self.current_move_index += 1
                
                # If there are more moves, play the opponent's response automatically
                if self.current_move_index < len(self.solution_moves):
                    # Get the opponent's move and convert to SAN before playing it
                    opponent_move_uci = self.solution_moves[self.current_move_index]
                    opponent_move = chess.Move.from_uci(opponent_move_uci)
                    
                    # Get SAN notation before playing the move
                    opponent_san = self.board.san(opponent_move)
                    
                    # Play the opponent's move
                    self.board.push(opponent_move)
                    self.current_move_index += 1
                    
                    # Tell the user what the opponent played
                    print(f"Opponent plays: {opponent_san}")
                    self.tts.speak(f"Opponent plays {opponent_san}")
                else:
                    print("🎉 Puzzle solved!")
                    self.tts.speak("Congratulations! You solved the puzzle!")
                    self.cleanup_html_file()
                    return True
            else:
                print("❌ Incorrect move")
                self.tts.speak("That's not the right move. Try again.")
                
        return True
        
    def do_another_puzzle_question(self):
        """Ask if user wants to do another puzzle and return True/False"""
        print("\n🎤 Listening for your response...")
        self.tts.speak("Would you like to solve another puzzle?")
        
        # Get response from voice using TTS engine directly
        try:
            response = self.tts.recognize_speech(timeout=5)
            
            if not response:
                print("No response detected, assuming no")
                return False
                
            print(f"You said: {response}")
            response_lower = response.lower().strip().rstrip('.')
            
            # Check for yes responses
            if any(word in response_lower for word in ["yes", "yeah", "yep", "sure", "okay", "ok"]):
                print("User wants another puzzle")
                return True
            # Check for no responses  
            elif any(word in response_lower for word in ["no", "nope", "exit", "stop", "quit", "done"]):
                print("User doesn't want another puzzle")
                return False
            else:
                print("Unclear response, assuming no")
                return False
                
        except Exception as e:
            print(f"Error getting response: {e}")
            return False

def play_puzzle_main(puzzle_settings):
    """Main entry point for playing a puzzle with theme cycling"""
    player = PuzzlePlayer()
    
    while True:
        # Get the next theme to prevent caching
        theme = player.get_next_theme()
        
        # Create puzzle settings with the current theme
        enhanced_settings = puzzle_settings.copy() if puzzle_settings else {}
        
        # Demo mode: Set first puzzle to easiest with random color
        if player.debug_mode and player.is_first_puzzle:
            enhanced_settings = {
                'difficulty': 'easiest',
                'color': random.choice(['white', 'black', None]),
                'theme': None
            }
            print(f"\n=== FETCHING PUZZLE ===")
            print(f"🎯 Difficulty: easiest")
            print(f"🎯 Color: {enhanced_settings['color']}")
            print(f"🎯 Theme: None")
        else:
            # Normal mode: use theme cycling
            enhanced_settings['theme'] = theme
            stats = player.get_theme_stats()
            print(f"\n=== FETCHING PUZZLE WITH THEME: {theme} ===")
            print(f"📊 Theme Stats: {stats['themes_used']}/{stats['total_themes']} themes used")
        
        # Fetch a new puzzle with the current theme
        from .fetch_type_of_puzzle import fetch_puzzle_with_settings
        puzzle_data = fetch_puzzle_with_settings(enhanced_settings)
        
        if not puzzle_data:
            print("❌ Failed to fetch puzzle")
            return False
            
        result = player.play_puzzle(puzzle_data)
        if result == False:
            return False
            
        # Ask if they want another puzzle
        if not player.do_another_puzzle_question():
            return False
    return True


