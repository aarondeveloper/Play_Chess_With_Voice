"""
Deepgram Speech Services voice recognition module for chess commands.
"""
import os
import pyaudio
import wave
import tempfile
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from dotenv import load_dotenv
from .chess_notation_parser_SAN import parse_chess_notation_san_to_uci

# Load environment variables
load_dotenv()

class DeepgramVoiceRecognizer:
    def __init__(self):
        """Initialize Deepgram Speech Service"""
        self.api_key = os.getenv('DEEPGRAM_API_KEY')
        
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
        
        # Initialize client (it will automatically use DEEPGRAM_API_KEY from environment)
        self.client = DeepgramClient()
        
        # Audio settings
        self.RATE = 16000
        self.CHUNK = 1024
        self.CHANNELS = 1
        self.FORMAT = pyaudio.paInt16

    def recognize_speech_simple(self, timeout=5):
        """
        Capture audio with pyaudio, save as WAV file, then analyze with Deepgram
        """
        print("Listening... Say a chess move now!")
        
        try:
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            print("Recording...")
            frames = []
            
            # Record for specified duration
            for _ in range(0, int(self.RATE / self.CHUNK * timeout)):
                data = stream.read(self.CHUNK)
                frames.append(data)
            
            print("Finished recording.")
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save audio to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_filename = temp_audio.name
                
                # Write WAV file
                with wave.open(temp_filename, 'wb') as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(frames))
            
            # Read the audio file and send to Deepgram
            with open(temp_filename, "rb") as file:
                buffer_data = file.read()

            payload: FileSource = {
                "buffer": buffer_data,
            }
            
            # Configure Deepgram options
            options = PrerecordedOptions(
                model="nova-3",
                language="en-US",
                smart_format=True,
                punctuate=True,
            )
            
            # Send to Deepgram for transcription
            response = self.client.listen.rest.v("1").transcribe_file(payload, options)
            
            # Clean up temporary file
            os.unlink(temp_filename)
            
            # Extract transcription
            if response.results and response.results.channels:
                transcript = response.results.channels[0].alternatives[0].transcript
                if transcript.strip():
                    print(f"You said: {transcript}")
                    return transcript
                else:
                    print("No speech detected")
                    return None
            else:
                print("No speech could be recognized")
                return None
                
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            # Try to clean up temp file if it exists
            try:
                if 'temp_filename' in locals():
                    os.unlink(temp_filename)
            except:
                pass
            return None

def process_chess_command(text, board_state=None):
    """Process a spoken chess command and convert it to a UCI move using SAN parser."""
    if not text:
        return None
        
    # Use the new SAN parser with board validation
    move = parse_chess_notation_san_to_uci(text, board_state)
    
    if move:
        print(f"✅ Parsed move: '{text}' -> '{move}' (validated against current position)")
        
        # Provide a more human-readable interpretation
        if move == "e1g1":
            print("Interpreted as: Castle kingside (white)")
        elif move == "e1c1":
            print("Interpreted as: Castle queenside (white)")
        elif move == "e8g8":
            print("Interpreted as: Castle kingside (black)")
        elif move == "e8c8":
            print("Interpreted as: Castle queenside (black)")
        elif len(move) == 4:
            print(f"Interpreted as: Move from {move[0:2]} to {move[2:4]}")
        elif len(move) == 5:  # Promotion
            promotion_piece = {'q': 'Queen', 'r': 'Rook', 'b': 'Bishop', 'n': 'Knight'}.get(move[4], move[4])
            print(f"Interpreted as: Move from {move[0:2]} to {move[2:4]} and promote to {promotion_piece}")
    else:
        print("❌ Could not parse this as a chess move.")
        print("Try saying something like:")
        print("- 'pawn to e4'")
        print("- 'knight to f3'")
        print("- 'pawn from g takes h5'")
        print("- 'castle kingside'")
        print("- 'pawn to e8 promote to queen'")
    
    return move

def get_chess_move_from_voice(board_state=None):
    """Complete process to get a chess move from voice input using Deepgram."""
    try:
        recognizer = DeepgramVoiceRecognizer()
        text = recognizer.recognize_speech_simple()
        return process_chess_command(text, board_state)
    except Exception as e:
        print(f"Error initializing Deepgram Speech Recognition: {e}")
        print("Please check your Deepgram API key in the .env file")
        return None 