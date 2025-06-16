"""Module for managing game flow and events"""
import berserk
import time
from .game_state import GameState
import threading
import queue
import os
from gtts import gTTS
import pygame

class GameManager:
    def __init__(self, client):
        self.client = client
        self.state = GameState()
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.is_speaking = False
        self.move_thread_active = False
        self.temp_files = []
        self.temp_count = 0
        
        # Initialize pygame mixer for audio
        pygame.mixer.init()
        
        # Start speech processing thread
        self.start_speech_thread()
        
        # Clean up any leftover temp files
        self._cleanup_temp_files()

    def _cleanup_temp_files(self):
        """Clean up any leftover speech files from previous runs"""
        for file in os.listdir():
            if file.startswith("gm_speech_") and file.endswith(".mp3"):
                try:
                    os.remove(file)
                    print(f"Removed leftover file: {file}")
                except Exception as e:
                    print(f"Could not remove leftover file {file}: {e}")

    def start_speech_thread(self):
        """Start the background speech thread"""
        def speech_worker():
            while True:
                try:
                    text = self.speech_queue.get()
                    if text is None:  # Shutdown signal
                        break
                    
                    # Generate a unique temp file name
                    temp_file = f"gm_speech_{self.temp_count}.mp3"
                    self.temp_count += 1
                    self.temp_files.append(temp_file)
                    
                    print(f"Creating speech file: {temp_file} with text: {text}")
                    
                    # Create and save the audio file
                    tts = gTTS(text=text, lang='en', slow=False)
                    tts.save(temp_file)
                    
                    # Ensure mixer is initialized
                    if not pygame.mixer.get_init():
                        print("Re-initializing pygame mixer")
                        pygame.mixer.init()
                    
                    # Play the audio with better error handling
                    try:
                        pygame.mixer.music.load(temp_file)
                        pygame.mixer.music.play()
                        print(f"Playing audio: {temp_file}")
                        
                        # Wait for playback to complete
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                        
                        print(f"Finished playing: {temp_file}")
                    except Exception as e:
                        print(f"Pygame audio error: {e}")
                    
                except Exception as e:
                    print(f"Speech worker error: {e}")
                finally:
                    self.speech_queue.task_done()
        
        self.speech_thread = threading.Thread(target=speech_worker, daemon=True)
        self.speech_thread.start()
        print("Speech thread started")

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
            print(f"Move: {move_info}")
            # Format the move for speech
            speech_text = san_move.replace("N", "night ") #N is knight, but we say night gTTS SUCKS LOL
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
        #self.speech_queue.join()

    def resign_game(self, game_id):
        """Resign the current game"""
        try:
            self.client.board.resign_game(game_id)
            self.speak_status("Resigning game")
            return True
        except Exception as e:
            print(f"Error resigning: {e}")
            return False

    def send_draw(self, game_id):
        """Handle draw offers"""
        try:
            self.client.board.offer_draw(game_id)
            self.speak_status("Offering draw")
            return True
        except Exception as e:
            print(f"Error with draw: {e}")
            return False
    def accept_draw(self, game_id):
        """Accept draw offers"""
        try:
            self.client.board.offer_draw(game_id)
            self.speak_status("Accepting draw")
            return True
        except Exception as e:
            print(f"Error with draw: {e}")
            return False

    def decline_draw(self, game_id):
        """Decline draw offers"""
        try:
            self.client.board.decline_draw(game_id)
            self.speak_status("Declining draw")
            return True
        except Exception as e:
            print(f"Error with draw: {e}")
            return False

    def handle_command(self, game_id, command):
        """Handle non-move commands like resign and draw"""
        if not command:
            return False
        
        if command == "EXIT":
            print("Exiting game...")
            self.resign_game(game_id)
            return True
        
        elif command == "resign":
            self.resign_game(game_id)
            return True
        
        elif command == "draw":
            self.send_draw(game_id)
            return False  # Continue listening after draw offer
        
        elif command == "accept draw":
            self.accept_draw(game_id)
            return False  # Continue listening if draw isn't accepted
        
        elif command == "decline draw":
            self.decline_draw(game_id)
            return False  # Continue listening after declining
        
        return None  # Not a command

    def make_move(self, game_id, move_function):
        """Make a move using the provided move function"""
        print("\nYour turn! Please speak your move...")
        while self.move_thread_active:
            if not self.move_thread_active:
                return False
            
            try:
                # Pass the current board state to the voice recognition function
                move = move_function(self.state.board)
                
                if not self.move_thread_active:
                    return False
                    
                if not move:
                    print("Couldn't understand the move. Please try again.")
                    self.speak_status("Speak up!")
                    continue
                
                # First check if it's a command
                command_result = self.handle_command(game_id, move)
                if command_result is not None:
                    return command_result
                
                # If not a command, try to make the move
                if not self.move_thread_active:
                    return False
                    
                self.client.board.make_move(game_id, move)
                print(f"Move {move} sent successfully!")
                return True
                
            except Exception as e:
                if not self.move_thread_active:
                    return False
                print(f"Error making move: {e}")
                #self.speak_status("Not a move")
                print("Please try again.")

    def stop_move_thread(self):
        """Stop the move input thread"""
        self.move_thread_active = False 

    def __del__(self):
        """Cleanup when object is destroyed"""
        # Signal speech thread to stop
        if hasattr(self, 'speech_queue'):
            self.speech_queue.put(None)
        
        # Clean up temp files
        if hasattr(self, 'temp_files'):
            for file in self.temp_files:
                try:
                    if os.path.exists(file):
                        os.remove(file)
                except Exception as e:
                    print(f"Error removing temp file: {e}")
        
        # Stop pygame mixer
        if pygame.mixer.get_init():
            pygame.mixer.quit() 