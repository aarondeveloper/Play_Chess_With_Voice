import berserk  # The Python client for Lichess API
import speech_recognition as sr
import pyttsx3
import threading
import time
import chess  # Python chess library to help with move validation
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VoiceChessController:
    def __init__(self):
        # Get API token from environment variables
        api_token = os.getenv("LICHESS_API_TOKEN")
        if not api_token:
            raise ValueError("LICHESS_API_TOKEN not found in environment variables")
        
        # Set up Lichess client
        self.session = berserk.TokenSession(api_token)
        self.client = berserk.Client(self.session)
        
        # Set up voice recognition
        self.recognizer = sr.Recognizer()
        
        # Set up text-to-speech
        self.tts_engine = pyttsx3.init()
        
        # Set up chess board for tracking state
        self.board = chess.Board()
        
        # Game state
        self.current_game = None
        self.is_my_turn = False
    
    def start_game(self, rated=False, clock_limit=5, clock_increment=3):
        """Create an open seek for anyone to accept"""
        self.speak("Creating a new game seek. Waiting for an opponent.")
        
        # Create an open seek using the board API
        # This is a streaming request that stays open
        seek_thread = threading.Thread(
            target=self._create_and_maintain_seek,
            args=(clock_limit, clock_increment, rated),
            daemon=True
        )
        seek_thread.start()
        
        # Start listening for game state updates in a separate thread
        event_thread = threading.Thread(
            target=self._listen_for_game_events,
            daemon=True
        )
        event_thread.start()

    def _create_and_maintain_seek(self, clock_limit, clock_increment, rated):
        """Create and maintain an open seek"""
        try:
            # Note: time must be in minutes (between 1 and 180)
            # clock_limit is already in minutes
            
            # Using the board.seek endpoint
            seek_response = self.client.board.seek(
                time=clock_limit,        # Already in minutes
                increment=clock_increment,  # In seconds
                rated=rated,
                variant='standard',
                color='random'
            )
            
            # Keep the connection open until a game starts or an exception occurs
            for _ in seek_response:
                # This keeps the connection open
                pass
            
        except Exception as e:
            self.speak(f"Error with seek: {str(e)}")

    def _listen_for_game_events(self):
        """Listen for game start events"""
        for event in self.client.board.stream_incoming_events():
            if event['type'] == 'gameStart':
                self.current_game = event['game']
                game_id = event['game']['gameId']
                color = event['game']['color']
                
                self.speak(f"Game started! You are playing as {color}.")
                
                # Initialize the board
                self.board = chess.Board()
                
                # Set initial turn based on color
                self.is_my_turn = (color == 'white')
                
                # Start streaming the game state
                game_thread = threading.Thread(
                    target=self.stream_game_state,
                    args=(game_id,),
                    daemon=True
                )
                game_thread.start()
                
                return

    def accept_challenge(self, challenge_id=None):
        """Accept a specific challenge or the first pending challenge"""
        if not challenge_id:
            # Get list of pending challenges
            challenges = self.client.challenges.get()
            incoming = [c for c in challenges['in'] if c['status'] == 'created']
            
            if not incoming:
                self.speak("No pending challenges found.")
                return False
            
            # Accept the first pending challenge
            challenge_id = incoming[0]['id']
        
        self.speak("Accepting challenge. Game will start soon.")
        self.client.challenges.accept(challenge_id)
        
        # Start listening for game state updates
        threading.Thread(target=self.stream_game_state, daemon=True).start()
        return True
    
    def stream_game_state(self, game_id):
        """Listen for game state updates from Lichess"""
        for event in self.client.board.stream_game_state(game_id):
            if 'state' in event:
                # Update local board
                if len(event['state']['moves']) > 0:
                    moves = event['state']['moves'].split()
                    if len(moves) > len(self.board.move_stack):
                        last_move = moves[-1]
                        # Update our local board
                        self.board.push_uci(last_move)
                        
                        # If it was opponent's move, announce it
                        if not self.is_my_turn:
                            self.speak(f"Opponent played {self.format_move_for_speech(last_move)}")
                        
                        # Toggle turn
                        self.is_my_turn = not self.is_my_turn
    
    def listen_for_move(self):
        """Listen for voice commands and execute moves"""
        with sr.Microphone() as source:
            self.speak("Your move. Speak now.")
            audio = self.recognizer.listen(source)
            
        try:
            command = self.recognizer.recognize_google(audio)
            move = self.parse_chess_notation(command)
            
            if move:
                # Make the move on Lichess
                self.client.board.make_move(self.current_game['id'], move)
                self.speak(f"Moving {self.format_move_for_speech(move)}")
            else:
                self.speak("I didn't understand that move. Please try again.")
                
        except Exception as e:
            self.speak(f"Error: {str(e)}")
    
    def parse_chess_notation(self, text):
        """Convert spoken chess notation to UCI format"""
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
                    
                    # Verify it's a legal move
                    try:
                        chess_move = chess.Move.from_uci(move)
                        if chess_move in self.board.legal_moves:
                            return move
                    except ValueError:
                        pass
        
        # If we couldn't parse the move
        print(f"Could not parse: {text}")
        return None

    def format_move_for_speech(self, uci_move):
        """Convert UCI move to spoken format"""
        if len(uci_move) < 4:
            return uci_move  # Return as is if it's not in the expected format
        
        from_square = uci_move[0:2]
        to_square = uci_move[2:4]
        
        # Get the piece type
        piece = self.board.piece_at(chess.parse_square(from_square))
        piece_name = "piece"
        if piece:
            piece_type = piece.piece_type
            if piece_type == chess.PAWN:
                piece_name = "pawn"
            elif piece_type == chess.KNIGHT:
                piece_name = "knight"
            elif piece_type == chess.BISHOP:
                piece_name = "bishop"
            elif piece_type == chess.ROOK:
                piece_name = "rook"
            elif piece_type == chess.QUEEN:
                piece_name = "queen"
            elif piece_type == chess.KING:
                piece_name = "king"
        
        return f"{piece_name} from {from_square} to {to_square}"
    
    def speak(self, text):
        """Use text-to-speech to communicate with the user"""
        print(text)  # Also print for debugging
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

# Example usage
if __name__ == "__main__":
    controller = VoiceChessController()
    controller.start_game()
    
    # Main game loop
    while True:
        if controller.is_my_turn:
            controller.listen_for_move()
        time.sleep(1) 