"""
Module for managing a Lichess game with voice control.
"""
import os
import berserk
from dotenv import load_dotenv
from .deepgram_voice_recognition import get_chess_move_from_voice
from .deepgram_challenge_voice_recognition import get_game_settings_from_voice
from .game_manager import GameManager
import time
from .deepgram_would_you_like_to_play_voice_recognition import ask_to_play
from .deepgram_do_you_want_solve_puzzles import ask_to_solve_puzzles
from .get_puzzle_type_from_voice import get_puzzle_settings_from_voice
from .fetch_type_of_puzzle import fetch_puzzle_with_settings
from .play_puzzle import play_puzzle_main
import threading

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
        print("=== Starting play_game ===")
        if not self.game_manager.wait_for_game_start(game_id):
            print("Game didn't start")
            return
            
        print("Starting to play...")
        time.sleep(0.5)
        
        move_thread = None
        
        try:
            for event in self.client.board.stream_game_state(game_id):
                print("\n========== EVENT DETAILS ==========")
                print(f"Event type: {event.get('type')}")
                print(f"Full event structure: {event}")
                
                result = self.game_manager.state.update_from_event(event)
                print(f"Update result: {result}")
                
                if isinstance(result, tuple):
                    if result[0] in ['checkmate', 'resign', 'draw']:
                        print("=== GAME END DETECTED ===")
                        print(f"End type: {result[0]}")
                        print(f"Winner: {result[1]}")
                        
                        print("Starting thread cleanup...")
                        self.game_manager.stop_move_thread()
                        print("Stop thread flag set")
                        
                        if move_thread and move_thread.is_alive():
                            print("Thread is alive, joining...")
                            move_thread.join(timeout=1.0)
                            print("Thread joined")
                        else:
                            print("No active thread to clean up")
                        
                        self.game_manager.process_game_end(result[0], result[1])
                        print("Game end processed")
                        time.sleep(2)
                        print("=== EXITING GAME ===")
                        return
                    else:
                        self.game_manager.announce_move(result)
                        time.sleep(0.5)
                
                # Start or stop move thread based on turn
                if self.game_manager.state.is_my_turn:
                    if move_thread is None or not move_thread.is_alive():
                        self.game_manager.move_thread_active = True
                        move_thread = threading.Thread(
                            target=self.game_manager.make_move,
                            args=(game_id, get_chess_move_from_voice)
                        )
                        move_thread.start()
                else:
                    # Stop move thread if it's not our turn
                    if move_thread and move_thread.is_alive():
                        self.game_manager.stop_move_thread()
                        move_thread.join(timeout=1.0)
                        move_thread = None
        finally:
            print("Stopping move thread")
            self.game_manager.stop_move_thread()
            if move_thread and move_thread.is_alive():
                move_thread.join(timeout=1.0)

def main():
    # """Main function to start and play games"""
    # game = LichessVoiceGame()
    
    while True:
        """Main function to start and play games"""
        game = LichessVoiceGame()
        print("\n=== CHESS VOICE COMMAND CENTER ===")
        
        # Ask if they want to play
        want_to_play = ask_to_play(game.game_manager)
        if want_to_play is False:  # They said no to chess
            # Ask if they want to solve puzzles instead
            puzzles = ask_to_solve_puzzles(game.game_manager)
            if puzzles is False:  # They said no to puzzles too
                break
            elif puzzles is True:  # They want puzzles
                print("Starting puzzle setup...")
                puzzle_settings = get_puzzle_settings_from_voice()
                print(f"Puzzle settings: {puzzle_settings}")
                
                # Fetch puzzle with settings
                puzzle_data = fetch_puzzle_with_settings(puzzle_settings)
                
                if puzzle_data:
                    # Start puzzle solving
                    play_puzzle_main(puzzle_data)
                else:
                    print("❌ Failed to fetch puzzle")
                break
            else:  # Unclear response about puzzles
                continue
        elif want_to_play is None:  # Unclear response about chess
            continue
        
        print("Starting game setup...")
        game_id = None
        # Get game settings through voice dialog
        debug = not True
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


    print("Thanks for playing! Goodbye.")

if __name__ == "__main__":
    main() 