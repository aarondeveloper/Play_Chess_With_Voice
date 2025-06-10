"""
Test script for Deepgram Speech Services integration
"""
from game.deepgram_voice_recognition import get_chess_move_from_voice, DeepgramVoiceRecognizer
import os

def test_deepgram_credentials():
    """Test if Deepgram credentials are properly set"""
    print("=== Testing Deepgram Speech Service Credentials ===")
    
    api_key = os.getenv('DEEPGRAM_API_KEY')
    
    if not api_key:
        print("❌ DEEPGRAM_API_KEY not found in environment variables")
        return False
        
    print("✅ Deepgram credentials found in environment")
    print(f"Key: {api_key[:8]}..." if len(api_key) > 8 else "Key: [SHORT KEY]")
    return True

def test_deepgram_voice_recognition():
    """Test Deepgram voice recognition for chess moves"""
    print("\n=== Testing Deepgram Voice Recognition ===")
    
    if not test_deepgram_credentials():
        print("Please add your Deepgram API key to the .env file:")
        print("DEEPGRAM_API_KEY=your_key_here")
        print("\nTo get a free API key:")
        print("1. Go to https://console.deepgram.com/")
        print("2. Sign up for a free account")
        print("3. Get 12,000 free minutes per month!")
        return
    
    try:
        recognizer = DeepgramVoiceRecognizer()
        print("✅ Deepgram Speech Service initialized successfully")
        
        print("\nSay a chess move (e.g., 'e2 to e4', 'castle kingside'):")
        move = get_chess_move_from_voice()
        
        if move:
            print(f"✅ Successfully recognized move: {move}")
        else:
            print("❌ Failed to recognize move")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if "credentials" in str(e).lower() or "api" in str(e).lower():
            print("Please check your Deepgram API key")

def continuous_test():
    """Run continuous voice recognition tests"""
    print("\n=== Continuous Deepgram Voice Recognition Test ===")
    print("Say chess moves continuously. Say 'exit' to stop.")
    
    if not test_deepgram_credentials():
        return
    
    try:
        while True:
            input("Press Enter when ready to speak a move...")
            move = get_chess_move_from_voice()
            
            if move == "EXIT":
                print("Exiting test...")
                break
            elif move:
                print(f"✅ Recognized: {move}")
            else:
                print("❌ Could not recognize move")
                
            print("-" * 50)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {e}")

def speed_test():
    """Test the speed of Deepgram recognition"""
    print("\n=== Deepgram Speed Test ===")
    
    if not test_deepgram_credentials():
        return
    
    try:
        recognizer = DeepgramVoiceRecognizer()
        
        for i in range(3):
            print(f"\nTest {i+1}/3: Say a chess move when ready...")
            input("Press Enter to start...")
            
            import time
            start_time = time.time()
            text = recognizer.recognize_speech_simple()
            end_time = time.time()
            
            if text:
                print(f"✅ Recognized: '{text}' in {end_time - start_time:.2f} seconds")
            else:
                print(f"❌ Failed to recognize in {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")

def test_audio_recording():
    """Test just the audio recording part without Deepgram"""
    print("\n=== Testing Audio Recording Only ===")
    
    try:
        import pyaudio
        import wave
        import tempfile
        
        # Audio settings
        RATE = 16000
        CHUNK = 1024
        CHANNELS = 1
        FORMAT = pyaudio.paInt16
        
        print("Testing microphone access...")
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("✅ Microphone access successful")
        print("Recording 3 seconds of audio...")
        
        frames = []
        for _ in range(0, int(RATE / CHUNK * 3)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("✅ Audio recorded successfully")
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Test saving to file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_filename = temp_audio.name
            
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
        
        print(f"✅ Audio saved to temporary file: {temp_filename}")
        
        # Clean up
        import os
        os.unlink(temp_filename)
        print("✅ Temporary file cleaned up")
        
    except Exception as e:
        print(f"❌ Audio recording test failed: {e}")

if __name__ == "__main__":
    print("🎙️ Deepgram Speech Services Test for Chess Voice Recognition")
    print("1. Test credentials")
    print("2. Single voice test")
    print("3. Continuous testing")
    print("4. Speed test")
    print("5. Test audio recording only")
    
    choice = input("Enter your choice (1-5): ").strip()
    
    if choice == "1":
        test_deepgram_credentials()
    elif choice == "3":
        continuous_test()
    elif choice == "4":
        speed_test()
    elif choice == "5":
        test_audio_recording()
    else:
        test_deepgram_voice_recognition() 