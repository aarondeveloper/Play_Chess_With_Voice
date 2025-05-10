"""
Module for managing a Lichess game with voice control.
"""
import os
import berserk
from dotenv import load_dotenv
from .chess_voice_recognition import get_chess_move_from_voice
from .game_manager import GameManager
import time

# Load environment variables
load_dotenv()
TOKEN = os.getenv('LICHESS_API_TOKEN')
OPPONENT = os.getenv('LICHESS_OPPONENT')

class LichessVoiceGame:
    def __init__(self):
        # Initialize Lichess client
        self.session = berserk.TokenSession(TOKEN)
        self.client = berserk.Client(self.session)
        self.game_manager = GameManager(self.client)
        
    def create_game(self):
        """Create a new game against the configured opponent"""
        try:
            # Create a challenge
            print(f"Creating challenge against {OPPONENT}...")
            challenge = self.client.challenges.create(
                username=OPPONENT,
                rated=False,
                clock_limit=300,  # 5 minutes
                clock_increment=3  # 3 second increment
            )
            
            game_id = challenge['id']
            print(f"Challenge created! Game ID: {game_id}")
            return game_id
            
        except berserk.exceptions.ResponseError as e:
            print(f"Failed to create game: {e}")
            return None
            
    def play_game(self, game_id):
        """Play a game using voice commands"""
        # Wait for game to start
        if not self.game_manager.wait_for_game_start(game_id):
            return
            
        print("Starting to play...")
        # Stream game state
        for event in self.client.board.stream_game_state(game_id):
            # Update game state and get last move if any
            last_move = self.game_manager.state.update_from_event(event)
            
            # Process opponent's move if any
            if last_move:
                self.game_manager.process_opponent_move(last_move)
                # Add a small delay after opponent's move
                #time.sleep(0.5)
            
            # Make our move if it's our turn
            if self.game_manager.state.is_my_turn:
                if not self.game_manager.make_move(game_id, get_chess_move_from_voice):
                    return
                # Add a small delay after our move
                #time.sleep(0.5)
            
            # Check if game is finished
            if self.game_manager.state.status == 'finished':
                print("\nGame Over!")
                break

def main():
    """Main function to start and play a game"""
    game = LichessVoiceGame()
    
    # Create a new game
    game_id = game.create_game()
    if not game_id:
        print("Failed to create game. Exiting.")
        return
        
    # Play the game
    game.play_game(game_id)

if __name__ == "__main__":
    main() 