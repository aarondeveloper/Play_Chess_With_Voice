"""
Module for playing chess puzzles with voice interaction.
"""
import chess
import chess.pgn
import io
from .deepgram_voice_recognition import get_chess_move_from_voice
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
        
    def get_user_move(self):
        """Get a move from the user via voice"""
        print("\n🎤 Listening for your move...")
        #self.tts.speak("Take your time to think. What is your move?")
        
        # Get move from voice (now with 60 second timeout)
        move_uci = get_chess_move_from_voice(self.board)
        
        if not move_uci:
            #self.tts.speak("I didn't catch that. Please speak clearly and try again.")
            return None
            
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
                
            # Check if it's correct
            if self.check_solution(user_move):
                print("✅ Correct move!")
                self.tts.speak("Correct!")
                
                # Make the move on the board
                self.board.push(user_move)
                self.current_move_index += 1
                
                # If there are more moves, describe the new position
                if self.current_move_index < len(self.solution_moves):
                    self.describe_board_position()
                else:
                    print("🎉 Puzzle solved!")
                    self.tts.speak("Congratulations! You solved the puzzle!")
                    return True
            else:
                print("❌ Incorrect move")
                self.tts.speak("That's not the right move. Try again.")
                
        return True

def play_puzzle_main(puzzle_data):
    """Main entry point for playing a puzzle"""
    player = PuzzlePlayer()
    return player.play_puzzle(puzzle_data)
