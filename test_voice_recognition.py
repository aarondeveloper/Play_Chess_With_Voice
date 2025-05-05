"""
Test module for chess voice recognition.
"""
from chess_voice_recognition import recognize_speech, process_chess_command

def test_voice_recognition():
    """Run a single voice recognition test"""
    print("Testing voice recognition for Lichess...")
    print("Please say a chess move when prompted (e.g., 'e2 to e4', 'Knight F3', 'castle kingside')")
    
    text = recognize_speech()
    if text:
        process_chess_command(text)
    
    return text

def continuous_test():
    """Run the voice recognition test in a loop with better timing"""
    print("Continuous voice recognition test for Lichess.")
    print("Say a chess move when ready, or 'exit' or 'quit' to stop.")
    
    while True:
        # Wait for user to press Enter before starting to listen
        input("Press Enter when you're ready to say a move...")
        
        text = recognize_speech()
        if not text:
            continue
            
        if 'exit' in text.lower() or 'quit' in text.lower():
            print("Exiting voice recognition test.")
            break
        
        process_chess_command(text)
        print("\n" + "-"*50)

if __name__ == "__main__":
    # Ask if user wants single test or continuous testing
    print("Voice Recognition Test")
    print("1. Single test")
    print("2. Continuous testing")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "2":
        continuous_test()
    else:
        test_voice_recognition() 