"""Module for managing game flow and events"""
import berserk
import time
from .game_state import GameState
import pyttsx3
import queue
import threading

class GameManager:
    def __init__(self, client):
        self.client = client
        self.state = GameState()
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.is_speaking = False
        
        # Start speech processing thread with fresh engine
        self.start_speech_thread()

    def start_speech_thread(self):
        """Start the background speech thread"""
        def speech_worker():
            engine = pyttsx3.init()
            while True:
                try:
                    text = self.speech_queue.get()
                    if text is None:  # Shutdown signal
                        break
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    print(f"Speech error: {e}")
                finally:
                    self.speech_queue.task_done()
        
        self.speech_thread = threading.Thread(target=speech_worker, daemon=True)
        self.speech_thread.start()

    def speak(self, text):
        """Add text to speech queue"""
        print(f"Speaking: {text}")
        self.speech_queue.put(text)

    def speak_status(self, text):
        """Queue status message for speech"""
        self.speak(text)

    def speak_move(self, text):
        """Queue move for speech"""
        self.speak(text)

    def wait_for_game_start(self, game_id):
        """Wait for game to start"""
        print(f"\nWaiting for opponent to accept game {game_id}...")
        
        for event in self.client.board.stream_incoming_events():
            print(f"Incoming Event: {event}")
            if event['type'] == 'gameStart' and event['game']['id'] == game_id:
                color = event['game']['color']
                self.state.set_color(color)
                self.speak_status(f"Game started! You are playing as {color}")
                return True
            elif event['type'] == 'challengeDeclined':
                print("Challenge was declined!")
                self.speak_status("Challenge was declined")
                return False
        return False

    def announce_move(self, move_info):
        """Process and announce a move"""
        if move_info and move_info[0] and move_info[1]:
            uci_move, san_move = move_info
            print("\n=== OPPONENT'S MOVE ===")
            
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

            print(f"Speaking: {speech_text}")
            
            # Use move engine for move announcements
            self.speak_move(speech_text)

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
        self.speak(message)
        # Wait for final message to be spoken
        self.speech_queue.join()

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