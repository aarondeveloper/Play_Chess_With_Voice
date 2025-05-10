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
        
    def create_game(self, max_retries=3):
        """Create a new game against the configured opponent"""
        for attempt in range(max_retries):
            try:
                print(f"Creating challenge against {OPPONENT}...")
                challenge = self.client.challenges.create(
                    username=OPPONENT,
                    rated=False,
                    clock_limit=300,
                    clock_increment=3
                )
                
                game_id = challenge['id']
                print(f"Challenge created! Game ID: {game_id}")
                return game_id
                
            except berserk.exceptions.ResponseError as e:
                if "Too Many Requests" in str(e):
                    wait_time = 30 if attempt == 0 else 60
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                print(f"Failed to create game: {e}")
                return None
                
        print("Max retries reached. Please try again later.")
        return None
            
    def play_game(self, game_id):
        """Play a game using voice commands"""
        # Wait for game to start
        if not self.game_manager.wait_for_game_start(game_id):
            return
            
        print("Starting to play...")
        #time.sleep(0.5)
        
        # Stream game state
        for event in self.client.board.stream_game_state(game_id):
            # Update game state and get last move or game end info
            result = self.game_manager.state.update_from_event(event)
            
            # Process opponent's move if any
            if isinstance(result, tuple):
                if result[0] in ['checkmate', 'resign', 'draw']:
                    # Handle game end
                    self.game_manager.process_game_end(result[0], result[1])
                    time.sleep(2)  # Give time for final announcement
                    print("Game finished, exiting...")
                    return  # Exit the game loop completely
                else:
                    # Normal move
                    self.game_manager.announce_move(result)
                    time.sleep(0.5)
            
            # Make our move if it's our turn
            if self.game_manager.state.is_my_turn:
                if not self.game_manager.make_move(game_id, get_chess_move_from_voice):
                    return
                time.sleep(0.5)

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