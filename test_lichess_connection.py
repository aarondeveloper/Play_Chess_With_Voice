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

def test_direct_challenge():
    """Test sending a direct challenge to a specific user defined in .env"""
    # Get API token and opponent username from environment variables
    api_token = os.getenv("LICHESS_API_TOKEN")
    opponent = os.getenv("LICHESS_OPPONENT")
    
    if not api_token:
        print("Error: LICHESS_API_TOKEN not found in environment variables")
        return False
    
    if not opponent:
        print("Error: LICHESS_OPPONENT not found in environment variables")
        print("Please add LICHESS_OPPONENT=username to your .env file")
        return False
    
    print("Testing Lichess API connection...")
    
    # Set up Lichess client
    session = berserk.TokenSession(api_token)
    client = berserk.Client(session)
    
    try:
        # Test API connection by getting account info
        account = client.account.get()
        print(f"Successfully connected to Lichess as: {account['username']}")
        
        # Create a challenge to a specific user
        print(f"Challenging {opponent}...")
        
        challenge = client.challenges.create(
            username=opponent,
            rated=False,
            clock_limit=1800,  # 30 minutes in seconds
            clock_increment=0,
            variant='standard',
            color='random'
        )
        
        print(f"Challenge created with ID: {challenge['id']}")
        print(f"Challenge URL: https://lichess.org/{challenge['id']}")
        print("Waiting for the opponent to accept the challenge...")
        
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
                elif event['type'] == 'challengeDeclined':
                    print(f"Challenge declined by {opponent}")
                    return None
            return None
        
        game_thread = threading.Thread(target=listen_for_game_start)
        game_thread.daemon = True
        game_thread.start()
        
        # Wait for the game to start or the challenge to be declined
        while game_thread.is_alive():
            time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nCancelled by user")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    # Ask the user what they want to test
    print("What would you like to test?")
    print("1. Create an open seek (anyone can accept)")
    print("2. Challenge a specific player (from .env)")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "2":
        test_direct_challenge()
    else:
        test_lichess_connection() 