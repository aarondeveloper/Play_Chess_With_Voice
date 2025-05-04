import berserk  # The Python client for Lichess API
import speech_recognition as sr
import pyttsx3
import threading
import time
import chess  # Python chess library to help with move validation

class VoiceChessController:
    def __init__(self, api_token):
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
    
    def start_game_against_bot(self, bot_id="maia1"):
        """Start a new game against a bot"""
        self.current_game = self.client.challenges.create_ai(level=1, clock_limit=300, clock_increment=3)
        self.speak(f"Game started. You are playing as {self.current_game['color']}.")
        
        # Start listening for game state updates
        threading.Thread(target=self.stream_game_state, daemon=True).start()
    
    def stream_game_state(self):
        """Listen for game state updates from Lichess"""
        for event in self.client.board.stream_game_state(self.current_game['id']):
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
        # This would need sophisticated parsing logic
        # For example, converting "Knight to e4" to "Ne4"
        # Then converting algebraic notation to UCI format
        # ...
        
    def format_move_for_speech(self, uci_move):
        """Convert UCI move to spoken format"""
        # Convert something like "e2e4" to "pawn from e2 to e4"
        # ...
        
    def speak(self, text):
        """Use text-to-speech to communicate with the user"""
        print(text)  # Also print for debugging
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

# Example usage
if __name__ == "__main__":
    controller = VoiceChessController("your_lichess_api_token")
    controller.start_game_against_bot()
    
    # Main game loop
    while True:
        if controller.is_my_turn:
            controller.listen_for_move()
        time.sleep(1) 