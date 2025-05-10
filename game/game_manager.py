"""Module for managing game flow and events"""
import berserk
import time
from .game_state import GameState
import pyttsx3

class GameManager:
    def __init__(self, client):
        self.client = client
        self.state = GameState()
        self.tts_engine = pyttsx3.init()  # Initialize text-to-speech
    
    def wait_for_game_start(self, game_id):
        """Wait for the game to start"""
        print(f"\nWaiting for opponent to accept game {game_id}...")
        
        for event in self.client.board.stream_incoming_events():
            if event['type'] == 'gameStart' and event['game']['id'] == game_id:
                # Set color and initial turn
                color = event['game']['color']
                self.state.set_color(color)
                
                # Announce game start
                self.tts_engine.say(f"Game started! You are playing as {color}")
                self.tts_engine.runAndWait()
                
                return True
            elif event['type'] == 'challengeDeclined':
                print("Challenge was declined!")
                self.tts_engine.say("Challenge was declined")
                self.tts_engine.runAndWait()
                return False
                
        return False
    
    def speak_move(self, san_move):
        """Convert SAN move to spoken format and say it"""
        # Format the move for speech
        speech_text = san_move.replace("N", "Knight ")
        speech_text = speech_text.replace("B", "Bishop ")
        speech_text = speech_text.replace("R", "Rook ")
        speech_text = speech_text.replace("Q", "Queen ")
        speech_text = speech_text.replace("K", "King ")
        speech_text = speech_text.replace("x", " takes ")
        speech_text = speech_text.replace("+", " check")
        speech_text = speech_text.replace("#", " checkmate")
        speech_text = speech_text.replace("O-O-O", "Castle queenside")
        speech_text = speech_text.replace("O-O", "Castle kingside")

        # Speak the move
        print(f"Speaking: {speech_text}")
        self.tts_engine.say(speech_text)
        self.tts_engine.runAndWait()

    def process_opponent_move(self, move_info):
        """Process and display opponent's move"""
        if move_info and move_info[0] and move_info[1]:
            uci_move, san_move = move_info
            print("\n=== OPPONENT'S MOVE ===")
            print(f"Opponent played: {san_move}")
            self.speak_move(san_move)
    
    def make_move(self, game_id, move_function):
        """Make a move using the provided move function"""
        print("\nYour turn! Please speak your move...")
        while True:
            try:
                move = move_function()
                
                if not move:
                    print("Couldn't understand the move. Please try again.")
                    continue
                    
                if move == "EXIT":
                    print("Exiting game...")
                    return False
                
                # Try to make the move
                self.client.board.make_move(game_id, move)
                print(f"Move {move} sent successfully!")
                return True
                
            except berserk.exceptions.ResponseError as e:
                print(f"Invalid move: {e}")
                print("Please try another move.")
            except Exception as e:
                print(f"Error making move: {e}")
                print("Please try again.")

    def process_game_end(self, end_type, winner):
        """Announce game end conditions"""
        if end_type == 'checkmate':
            message = "Checkmate! "
            message += "You won!" if winner == self.state.my_color else "You lost."
        elif end_type == 'resign':
            message = "Game over by resignation. "
            message += "You won!" if winner == self.state.my_color else "Your opponent resigned."
        elif end_type == 'draw':
            message = "Game drawn!"
        
        print(f"\n=== GAME OVER ===\n{message}")
        self.tts_engine.say(message)
        self.tts_engine.runAndWait() 