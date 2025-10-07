"""
Module for fetching chess puzzles from Lichess API with voice-controlled criteria.
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PuzzleFetcher:
    def __init__(self):
        """Initialize the puzzle fetcher with Lichess API token"""
        self.token = os.getenv('LICHESS_API_TOKEN')
        self.base_url = "https://lichess.org/api/puzzle/next"
        
    def fetch_puzzle(self, difficulty="normal", color=None, theme=None):
        """
        Fetch a random puzzle from Lichess with specified criteria
        
        Args:
            difficulty (str): "easiest", "easier", "normal", "harder", "hardest"
            color (str): "white", "black", or None for random
            theme (str): Puzzle theme (optional)
            
        Returns:
            dict: Puzzle data or None if failed
        """
        try:
            # Build the request URL
            url = self.base_url
            
            # Add query parameters
            params = {
                "difficulty": difficulty
            }
            
            if color:
                params["color"] = color
                
            if theme:
                params["angle"] = theme
                
            # Add cache-busting parameter to ensure different puzzles
            import time
            params["_t"] = int(time.time())
                
            # Set up headers with authentication
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
                print(f"Using authentication token: {self.token[:10]}...")
                
                # Test if token has puzzle access
                try:
                    test_response = requests.get("https://lichess.org/api/account", headers=headers)
                    if test_response.status_code == 200:
                        print("✅ Token is valid and authenticated")
                    else:
                        print(f"⚠️ Token may not have puzzle:read scope (status: {test_response.status_code})")
                except:
                    print("⚠️ Could not verify token permissions")
            else:
                print("⚠️ No Lichess API token found - puzzles may be repeated")
                
            print(f"Fetching puzzle with criteria: {params}")
            print(f"Request URL: {url}")
            print(f"Full request: {url}?{requests.compat.urlencode(params)}")
            
            # Make the API request
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                puzzle_data = response.json()
                print(f"✅ Puzzle fetched successfully!")
                print(f"Puzzle ID: {puzzle_data['puzzle']['id']}")
                print(f"Rating: {puzzle_data['puzzle']['rating']}")
                print(f"Themes: {puzzle_data['puzzle']['themes']}")
                
                # Check if we got the same puzzle ID as before
                if hasattr(self, 'last_puzzle_id'):
                    if puzzle_data['puzzle']['id'] == self.last_puzzle_id:
                        print("⚠️ WARNING: Same puzzle ID as before - token may not have puzzle:read scope")
                    else:
                        print("✅ Different puzzle ID - token working correctly")
                self.last_puzzle_id = puzzle_data['puzzle']['id']
                
                return puzzle_data
            else:
                print(f"❌ Failed to fetch puzzle: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching puzzle: {e}")
            return None
            
    def get_puzzle_info(self, puzzle_data):
        """Extract key information from puzzle data"""
        if not puzzle_data:
            return None
            
        puzzle = puzzle_data.get('puzzle', {})
        game = puzzle_data.get('game', {})
        
        return {
            'id': puzzle.get('id'),
            'rating': puzzle.get('rating'),
            'themes': puzzle.get('themes', []),
            'solution': puzzle.get('solution', []),
            'plays': puzzle.get('plays'),
            'game_id': game.get('id'),
            'players': game.get('players', []),
            'pgn': game.get('pgn', '')
        }

def fetch_puzzle_with_settings(puzzle_settings=None):
    """Fetch a puzzle with the given settings"""
    print("\n=== FETCHING PUZZLE ===")
    
    fetcher = PuzzleFetcher()
    
    # Fetch puzzle with settings
    if puzzle_settings:
        puzzle_data = fetcher.fetch_puzzle(
            difficulty=puzzle_settings.get('difficulty', 'normal'),
            color=puzzle_settings.get('color'),
            theme=puzzle_settings.get('theme')
        )
    else:
        puzzle_data = fetcher.fetch_puzzle()
    
    if puzzle_data:
        info = fetcher.get_puzzle_info(puzzle_data)
        print(f"\n🎯 Puzzle Fetched Successfully!")
        print(f"Rating: {info['rating']}")
        print(f"Themes: {', '.join(info['themes'])}")
        #print(f"Solution moves: {len(info['solution'])}")
        return puzzle_data
        
    else:
        print("❌ Failed to fetch puzzle. Please try again.")
        return None
