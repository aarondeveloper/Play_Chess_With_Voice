"""Module for managing game flow and events"""
import berserk
import time
from .game_state import GameState

class GameManager:
    def __init__(self, client):
        self.client = client
        self.state = GameState()
    
    def wait_for_game_start(self, game_id):
        """Wait for the game to start"""
        print(f"\nWaiting for opponent to accept game {game_id}...")
        
        for event in self.client.board.stream_incoming_events():
            if event['type'] == 'gameStart' and event['game']['id'] == game_id:
                # Set color and initial turn
                self.state.set_color(event['game']['color'])
                return True
            elif event['type'] == 'challengeDeclined':
                print("Challenge was declined!")
                return False
                
        return False
    
    def process_opponent_move(self, move):
        """Process and display opponent's move"""
        if move:
            print(f"\nOpponent played: {move}")
            # Add a small delay to ensure the message is seen
            time.sleep(1)
    
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