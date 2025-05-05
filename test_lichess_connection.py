import berserk
import time
import chess
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_lichess_connection():
    # Get API token from environment variables
    api_token = os.getenv("LICHESS_API_TOKEN")
    
    if not api_token:
        print("Error: LICHESS_API_TOKEN not found in environment variables")
        return False
    
    print("Testing Lichess API connection...")
    
    # Set up Lichess client
    session = berserk.TokenSession(api_token)
    client = berserk.Client(session)
    
    try:
        # Test API connection by getting account info
        account = client.account.get()
        print(f"Successfully connected to Lichess as: {account['username']}")
        
        # Create an open seek instead of a direct challenge
        print("Creating an open seek...")
        
        # Using the board.seek endpoint instead of challenges.create
        # This is a streaming request that stays open
        # Note: time is in minutes (must be between 1 and 180)
        seek_response = client.board.seek(
            time=30,
            increment=0,           # 5 minutes (not seconds!)     
            rated=False,      # Casual game
            variant='standard',
            color='random'
        )
        
        print("Seek created. Waiting for an opponent to accept...")
        print("Open another browser and go to lichess.org to see your seek")
        print("Press Ctrl+C to cancel the seek")
        
        # Start a separate thread to listen for game events
        import threading
        
        def listen_for_game_start():
            print("Listening for game events...")
            for event in client.board.stream_incoming_events():
                if event['type'] == 'gameStart':
                    game_id = event['game']['gameId']
                    print(f"Game started! Game ID: {game_id}")
                    print(f"Game URL: https://lichess.org/{game_id}")
                    return game_id
            return None
        
        game_thread = threading.Thread(target=listen_for_game_start)
        game_thread.daemon = True
        game_thread.start()
        
        # Keep the seek connection open
        for _ in seek_response:
            # This will keep the connection open until someone accepts
            # or until the user cancels with Ctrl+C
            pass
                
    except KeyboardInterrupt:
        print("\nSeek cancelled by user")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_lichess_connection() 