"""
Module for playing chess puzzles with voice interaction.
"""
import chess
import chess.pgn
import io
from .deepgram_voice_recognition import get_chess_move_from_voice, DeepgramVoiceRecognizer
from .deepgram_challenge_voice_recognition import DeepgramChallengeTTS
from .chess_notation_parser_SAN import parse_chess_notation_san_to_uci

class PuzzlePlayer:
    def __init__(self):
        """Initialize the puzzle player with TTS"""
        self.tts = DeepgramChallengeTTS()
        self.board = None
        self.solution_moves = []
        self.current_move_index = 0
        
    def setup_puzzle(self, puzzle_data):
        """Set up the puzzle board and solution"""
        if not puzzle_data:
            return False
            
        # Create a new board
        self.board = chess.Board()
        
        # Get the PGN from the game
        pgn = puzzle_data.get('game', {}).get('pgn', '')
        if not pgn:
            print("❌ No PGN found in puzzle data")
            return False
            
        # Parse the PGN to get all moves
        pgn_io = io.StringIO(pgn)
        game = chess.pgn.read_game(pgn_io)
        
        if not game:
            print("❌ Could not parse PGN")
            return False
            
        # Play all moves up to the puzzle position
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
            
        # Set our board to the puzzle position
        self.board = board
        
        # Get the solution moves
        self.solution_moves = puzzle_data.get('puzzle', {}).get('solution', [])
        self.current_move_index = 0
        
        print(f"✅ Puzzle setup complete!")
        print(f"Solution moves: {self.solution_moves}")
        return True
        
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
        
        # Speak each part with pauses for more natural speech
        for part in description_parts:
            self.tts.speak(part)
            # Add a small pause between parts
            import time
            time.sleep(0.5)
        
        self.tts.speak("Take your time to think. What is your move?")
        self.tts.speak("At any point you can say 'exit puzzle' to quit")
        
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
    """Main entry point for playing a puzzle"""
    while True:
        # Fetch a new puzzle each time
        from .fetch_type_of_puzzle import fetch_puzzle_with_settings
        puzzle_data = fetch_puzzle_with_settings(puzzle_settings)
        
        if not puzzle_data:
            print("❌ Failed to fetch puzzle")
            return False
            
        player = PuzzlePlayer()
        result = player.play_puzzle(puzzle_data)
        if result == False:
            return False
            
        # Ask if they want another puzzle
        if not player.do_another_puzzle_question():
            return False
    return True
