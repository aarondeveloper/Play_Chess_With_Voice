"""
Module for managing a Lichess game with voice control.
"""
import os
import berserk
from dotenv import load_dotenv
from .chess_voice_recognition import get_chess_move_from_voice
from .create_challenge_voice_recognition import get_game_settings_from_voice
from .game_manager import GameManager
import time
import speech_recognition as sr
from .would_you_like_to_play_voice_recognition import ask_to_play

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
        
    def create_game_with_settings(self, settings, max_retries=3):
        """Create a new game with specified settings"""
        if not settings:
            return None
        
        for attempt in range(max_retries):
            try:
                # Handle open challenges
                if settings.get('is_open', False):
                    return self._create_open_challenge(settings)
                # Handle direct challenges
                else:
                    return self._create_direct_challenge(settings)
                
            except berserk.exceptions.ResponseError as e:
                if "Too Many Requests" in str(e):
                    wait_time = 30 if attempt == 0 else 60
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    self.game_manager.speak_status("Rate limited. Please wait.")
                    time.sleep(wait_time)
                    continue
                print(f"Failed to create game: {e}")
                self.game_manager.speak_status("Failed to create game")
                return None
        
        print("Max retries reached. Please try again later.")
        self.game_manager.speak_status("Failed to create game after multiple attempts")
        return None

    def _create_open_challenge(self, settings):
        """Create an open challenge on Lichess"""
        print("\nCreating an open challenge...")
        self.game_manager.speak_status("Creating open challenge")
        print("Finished speaking status")
        try:
            # Create the seek - this returns how long it took
            seek_time = self.client.board.seek(
                time=settings.get('time_control', 5),
                increment=settings.get('increment', 3),
                rated=settings.get('rated', False),
                variant='standard',
                color='random'
            )
            print(f"Seek created in {seek_time} seconds")
            
            # Now listen for someone to accept
            print("Waiting for opponent...")
            for event in self.client.board.stream_incoming_events():
                print(f"Event received: {event}")
                if event.get('type') == 'gameStart':
                    print("Game starting!")
                    return event['game']['id']
        except KeyboardInterrupt:
            print("\nCancelling seek...")
            self.client.board.cancel_seek()  # Cancel the seek
            return None
        except Exception as e:
            print(f"Error in seek: {e}")
            self.client.board.cancel_seek()  # Cancel on error too
            return None
        
        return None

    def _create_direct_challenge(self, settings):
        """Create a direct challenge to a specific player"""
        opponent = settings.get('opponent', OPPONENT)
        print(f"\nCreating challenge against {opponent}...")
        self.game_manager.speak_status(f"Challenging {opponent}")
        challenge = self.client.challenges.create(
            username=opponent,
            rated=settings.get('rated', False),
            clock_limit=settings.get('time_control', 5) * 60,  # Convert to seconds
            clock_increment=settings.get('increment', 3),
            variant='standard',
            color='random'
        )
        return challenge['id']
            
    def play_game(self, game_id):
        """Play a game using voice commands"""
        # Wait for game to start
        if not self.game_manager.wait_for_game_start(game_id):
            return
            
        print("Starting to play...")
        time.sleep(0.5)
        
        # Stream game state
        for event in self.client.board.stream_game_state(game_id):
            # Enhanced debugging for events
            print("\n========== EVENT DETAILS ==========")
            print(f"Event type: {event.get('type')}")
            print(f"Full event structure: {event}")
            
            if 'drawOffer' in event:
                print(f"DRAW OFFER DETECTED: {event['drawOffer']}")
                print(f"Current player color: {self.game_manager.state.my_color}")
            
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

def main(debug=False):
    # """Main function to start and play games"""
    # game = LichessVoiceGame()
    
    while True:
        """Main function to start and play games"""
        game = LichessVoiceGame()
        print("\n=== CHESS VOICE COMMAND CENTER ===")
        
        # Ask if they want to play
        want_to_play = ask_to_play(game.game_manager)
        if want_to_play is False:  # They said no
            break
        elif want_to_play is None:  # Unclear response
            continue
        
        print("Starting game setup...")
        game_id = None
        # Get game settings through voice dialog
        if debug:
            settings = get_game_settings_from_voice()
            game_id = game.create_game_with_settings(settings)
        else:
            challenge = game.client.challenges.create(
            username="Iamthedon",
            rated=False,
            clock_limit=5 * 60,  # Convert to seconds
            clock_increment=3,
            variant='standard',
            color='random'
        )
            game_id = challenge['id']
        # if not settings:
        #     print("Failed to get game settings. Try again.")
        #     continue
            
        if not game_id:
            print("Failed to create game. Try again.")
            continue
        
        # Play the game
        game.play_game(game_id)
        
        print("\nGame finished. Starting new game setup...")
        time.sleep(1)  # Brief pause before next game setup

if __name__ == "__main__":
    main() 