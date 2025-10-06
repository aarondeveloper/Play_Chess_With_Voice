#!/usr/bin/env python3
"""
Test script to verify anti-caching strategies for puzzle fetching.
This script tests various cache-busting techniques without modifying existing code.
"""

import requests
import time
import random
import uuid
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AntiCacheTester:
    def __init__(self):
        """Initialize the anti-cache tester"""
        self.token = os.getenv('LICHESS_API_TOKEN')
        self.base_url = "https://lichess.org/api/puzzle/next"
        self.seen_puzzles = set()
        self.session_id = hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:8]
    
    def get_anti_cache_headers(self):
        """Generate comprehensive anti-caching headers"""
        return {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "If-None-Match": "*",
            "If-Modified-Since": "Thu, 01 Jan 1970 00:00:00 GMT",
            "User-Agent": f"ChessVoiceApp/{random.randint(1,100)}.{random.randint(1,100)}"
        }
    
    def get_cache_busting_params(self):
        """Generate multiple cache-busting parameters"""
        current_time = time.time()
        return {
            "_t": int(current_time),
            "_r": random.randint(1000, 9999),
            "_uuid": str(uuid.uuid4())[:8],
            "_ms": int(current_time * 1000),
            "_session": self.session_id,
            "_rand": random.randint(1, 999999)
        }
    
    def fetch_puzzle_with_anti_cache(self, difficulty="normal", color=None, theme=None):
        """Fetch a puzzle with comprehensive anti-caching"""
        try:
            # Build the request URL with cache-busting
            url = f"{self.base_url}?v={int(time.time())}"
            
            # Add query parameters
            params = {
                "difficulty": difficulty
            }
            
            if color:
                params["color"] = color
                
            if theme:
                params["angle"] = theme
                
            # Add comprehensive cache-busting parameters
            params.update(self.get_cache_busting_params())
                
            # Set up headers with authentication and anti-caching
            headers = self.get_anti_cache_headers()
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
                print(f"Using authentication token: {self.token[:10]}...")
            else:
                print("⚠️ No Lichess API token found - puzzles may be repeated")
                
            print(f"Fetching puzzle with criteria: {params}")
            print(f"Request URL: {url}")
            
            # Add random delay to prevent rapid-fire requests
            time.sleep(random.uniform(0.5, 1.5))
            
            # Make the API request
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                puzzle_data = response.json()
                puzzle_id = puzzle_data['puzzle']['id']
                print(f"✅ Puzzle fetched successfully! ID: {puzzle_id}")
                return puzzle_data
            else:
                print(f"❌ Failed to fetch puzzle: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching puzzle: {e}")
            return None
    
    def test_basic_fetch(self):
        """Test basic puzzle fetching"""
        print("\n🧪 Test 1: Basic Puzzle Fetching")
        print("-" * 40)
        
        puzzle_data = self.fetch_puzzle_with_anti_cache()
        if puzzle_data:
            puzzle_id = puzzle_data['puzzle']['id']
            rating = puzzle_data['puzzle']['rating']
            themes = puzzle_data['puzzle']['themes']
            print(f"✅ Successfully fetched puzzle:")
            print(f"   ID: {puzzle_id}")
            print(f"   Rating: {rating}")
            print(f"   Themes: {', '.join(themes)}")
            return puzzle_id
        else:
            print("❌ Failed to fetch puzzle")
            return None
    
    def test_multiple_fetches(self, count=5):
        """Test multiple puzzle fetches to check for uniqueness"""
        print(f"\n🧪 Test 2: Multiple Fetches ({count} puzzles)")
        print("-" * 40)
        
        puzzle_ids = []
        
        for i in range(count):
            print(f"\n--- Fetch #{i+1} ---")
            puzzle_data = self.fetch_puzzle_with_anti_cache()
            
            if puzzle_data:
                puzzle_id = puzzle_data['puzzle']['id']
                puzzle_ids.append(puzzle_id)
                print(f"✅ Got puzzle ID: {puzzle_id}")
                
                # Check if we've seen this puzzle before
                if puzzle_id in self.seen_puzzles:
                    print(f"⚠️ DUPLICATE: We've seen puzzle {puzzle_id} before!")
                else:
                    print(f"✅ NEW: First time seeing puzzle {puzzle_id}")
                    self.seen_puzzles.add(puzzle_id)
            else:
                print(f"❌ Failed to fetch puzzle #{i+1}")
        
        # Analyze results
        unique_ids = set(puzzle_ids)
        print(f"\n📊 Results:")
        print(f"Total puzzles fetched: {len(puzzle_ids)}")
        print(f"Unique puzzle IDs: {len(unique_ids)}")
        print(f"Total unique puzzles seen: {len(self.seen_puzzles)}")
        
        if len(unique_ids) == len(puzzle_ids):
            print("✅ SUCCESS: All puzzles are unique!")
            return True
        else:
            duplicates = len(puzzle_ids) - len(unique_ids)
            print(f"⚠️ WARNING: {duplicates} duplicate(s) found")
            return False
    
    def test_different_settings(self):
        """Test fetching puzzles with different settings"""
        print(f"\n🧪 Test 3: Different Settings")
        print("-" * 40)
        
        settings = [
            {"difficulty": "easiest", "color": None, "theme": None},
            {"difficulty": "normal", "color": "white", "theme": None},
            {"difficulty": "harder", "color": "black", "theme": None},
            {"difficulty": "normal", "color": None, "theme": "endgame"}
        ]
        
        results = []
        
        for i, setting in enumerate(settings):
            print(f"\n--- Setting #{i+1}: {setting} ---")
            puzzle_data = self.fetch_puzzle_with_anti_cache(**setting)
            
            if puzzle_data:
                puzzle_id = puzzle_data['puzzle']['id']
                rating = puzzle_data['puzzle']['rating']
                print(f"✅ Got puzzle ID: {puzzle_id}, Rating: {rating}")
                results.append(puzzle_id)
            else:
                print(f"❌ Failed to fetch puzzle with settings: {setting}")
                results.append(None)
        
        return results
    
    def test_cache_busting_parameters(self):
        """Test that cache-busting parameters are working"""
        print(f"\n🧪 Test 4: Cache-Busting Parameters")
        print("-" * 40)
        
        # Test headers
        headers = self.get_anti_cache_headers()
        print("Anti-cache headers:")
        for key, value in headers.items():
            print(f"  {key}: {value}")
        
        # Test parameters
        params = self.get_cache_busting_params()
        print("\nCache-busting parameters:")
        for key, value in params.items():
            print(f"  {key}: {value}")
        
        # Test that parameters change between calls
        print("\nTesting parameter uniqueness:")
        params1 = self.get_cache_busting_params()
        time.sleep(0.1)  # Small delay
        params2 = self.get_cache_busting_params()
        
        changes = []
        for key in params1:
            if key in params2:
                changed = params1[key] != params2[key]
                changes.append((key, changed))
                print(f"  {key} changed: {changed}")
        
        unique_changes = sum(1 for _, changed in changes if changed)
        print(f"\nParameters that changed: {unique_changes}/{len(changes)}")
        
        return unique_changes > 0
    
    def test_difficulty_cycling(self):
        """Test cycling through different difficulties to avoid caching"""
        print(f"\n🧪 Test 5: Difficulty Cycling (easiest -> normal -> harder -> easiest)")
        print("-" * 60)
        
        # Pattern: easiest -> normal -> harder -> easiest -> normal
        difficulty_cycle = ["easiest", "normal", "harder", "easiest", "normal"]
        puzzle_ids = []
        
        for i, difficulty in enumerate(difficulty_cycle):
            print(f"\n--- Cycle #{i+1}: {difficulty} ---")
            puzzle_data = self.fetch_puzzle_with_anti_cache(difficulty=difficulty)
            
            if puzzle_data:
                puzzle_id = puzzle_data['puzzle']['id']
                rating = puzzle_data['puzzle']['rating']
                puzzle_ids.append(puzzle_id)
                print(f"✅ Got puzzle ID: {puzzle_id}, Rating: {rating}")
                
                # Check if we've seen this puzzle before
                if puzzle_id in self.seen_puzzles:
                    print(f"⚠️ DUPLICATE: We've seen puzzle {puzzle_id} before!")
                else:
                    print(f"✅ NEW: First time seeing puzzle {puzzle_id}")
                    self.seen_puzzles.add(puzzle_id)
            else:
                print(f"❌ Failed to fetch puzzle with difficulty: {difficulty}")
                puzzle_ids.append(None)
        
        # Analyze results
        valid_puzzles = [pid for pid in puzzle_ids if pid is not None]
        unique_ids = set(valid_puzzles)
        
        print(f"\n📊 Difficulty Cycling Results:")
        print(f"Total puzzles fetched: {len(valid_puzzles)}")
        print(f"Unique puzzle IDs: {len(unique_ids)}")
        print(f"Total unique puzzles seen: {len(self.seen_puzzles)}")
        
        if len(unique_ids) == len(valid_puzzles):
            print("✅ SUCCESS: All puzzles are unique!")
            return True
        else:
            duplicates = len(valid_puzzles) - len(unique_ids)
            print(f"⚠️ WARNING: {duplicates} duplicate(s) found")
            return False
    
    def test_color_cycling(self):
        """Test cycling through different colors while keeping difficulty the same"""
        print(f"\n🧪 Test 6: Color Cycling (Same Difficulty)")
        print("-" * 50)
        
        # Keep difficulty the same, cycle through colors
        color_cycle = [None, "white", "black", None, "white", "black"]
        puzzle_ids = []
        
        for i, color in enumerate(color_cycle):
            print(f"\n--- Color Cycle #{i+1}: {color} ---")
            puzzle_data = self.fetch_puzzle_with_anti_cache(difficulty="normal", color=color)
            
            if puzzle_data:
                puzzle_id = puzzle_data['puzzle']['id']
                rating = puzzle_data['puzzle']['rating']
                puzzle_ids.append(puzzle_id)
                print(f"✅ Got puzzle ID: {puzzle_id}, Rating: {rating}")
                
                # Check if we've seen this puzzle before
                if puzzle_id in self.seen_puzzles:
                    print(f"⚠️ DUPLICATE: We've seen puzzle {puzzle_id} before!")
                else:
                    print(f"✅ NEW: First time seeing puzzle {puzzle_id}")
                    self.seen_puzzles.add(puzzle_id)
            else:
                print(f"❌ Failed to fetch puzzle with color: {color}")
                puzzle_ids.append(None)
        
        # Analyze results
        valid_puzzles = [pid for pid in puzzle_ids if pid is not None]
        unique_ids = set(valid_puzzles)
        
        print(f"\n📊 Color Cycling Results:")
        print(f"Total puzzles fetched: {len(valid_puzzles)}")
        print(f"Unique puzzle IDs: {len(unique_ids)}")
        print(f"Total unique puzzles seen: {len(self.seen_puzzles)}")
        
        if len(unique_ids) == len(valid_puzzles):
            print("✅ SUCCESS: All puzzles are unique!")
            return True
        else:
            duplicates = len(valid_puzzles) - len(unique_ids)
            print(f"⚠️ WARNING: {duplicates} duplicate(s) found")
            return False
    
    def test_theme_cycling(self):
        """Test cycling through different themes while keeping difficulty the same"""
        print(f"\n🧪 Test 7: Theme Cycling (Same Difficulty)")
        print("-" * 50)
        
        # Keep difficulty the same, cycle through themes
        theme_cycle = [None, "endgame", "tactics", "opening", "middlegame", None]
        puzzle_ids = []
        
        for i, theme in enumerate(theme_cycle):
            print(f"\n--- Theme Cycle #{i+1}: {theme} ---")
            puzzle_data = self.fetch_puzzle_with_anti_cache(difficulty="normal", theme=theme)
            
            if puzzle_data:
                puzzle_id = puzzle_data['puzzle']['id']
                rating = puzzle_data['puzzle']['rating']
                puzzle_ids.append(puzzle_id)
                print(f"✅ Got puzzle ID: {puzzle_id}, Rating: {rating}")
                
                # Check if we've seen this puzzle before
                if puzzle_id in self.seen_puzzles:
                    print(f"⚠️ DUPLICATE: We've seen puzzle {puzzle_id} before!")
                else:
                    print(f"✅ NEW: First time seeing puzzle {puzzle_id}")
                    self.seen_puzzles.add(puzzle_id)
            else:
                print(f"❌ Failed to fetch puzzle with theme: {theme}")
                puzzle_ids.append(None)
        
        # Analyze results
        valid_puzzles = [pid for pid in puzzle_ids if pid is not None]
        unique_ids = set(valid_puzzles)
        
        print(f"\n📊 Theme Cycling Results:")
        print(f"Total puzzles fetched: {len(valid_puzzles)}")
        print(f"Unique puzzle IDs: {len(unique_ids)}")
        print(f"Total unique puzzles seen: {len(self.seen_puzzles)}")
        
        if len(unique_ids) == len(valid_puzzles):
            print("✅ SUCCESS: All puzzles are unique!")
            return True
        else:
            duplicates = len(valid_puzzles) - len(unique_ids)
            print(f"⚠️ WARNING: {duplicates} duplicate(s) found")
            return False

    def test_parameter_variation(self):
        """Test varying parameters to break caching"""
        print(f"\n🧪 Test 8: Parameter Variation")
        print("-" * 40)
        
        # Test with slight parameter variations
        variations = [
            {"difficulty": "normal", "color": None},
            {"difficulty": "normal", "color": "white"},
            {"difficulty": "normal", "color": "black"},
            {"difficulty": "normal", "color": None, "theme": "endgame"},
            {"difficulty": "normal", "color": None, "theme": "tactics"}
        ]
        
        puzzle_ids = []
        
        for i, variation in enumerate(variations):
            print(f"\n--- Variation #{i+1}: {variation} ---")
            puzzle_data = self.fetch_puzzle_with_anti_cache(**variation)
            
            if puzzle_data:
                puzzle_id = puzzle_data['puzzle']['id']
                rating = puzzle_data['puzzle']['rating']
                puzzle_ids.append(puzzle_id)
                print(f"✅ Got puzzle ID: {puzzle_id}, Rating: {rating}")
                
                if puzzle_id in self.seen_puzzles:
                    print(f"⚠️ DUPLICATE: We've seen puzzle {puzzle_id} before!")
                else:
                    print(f"✅ NEW: First time seeing puzzle {puzzle_id}")
                    self.seen_puzzles.add(puzzle_id)
            else:
                print(f"❌ Failed to fetch puzzle with variation: {variation}")
                puzzle_ids.append(None)
        
        # Analyze results
        valid_puzzles = [pid for pid in puzzle_ids if pid is not None]
        unique_ids = set(valid_puzzles)
        
        print(f"\n📊 Parameter Variation Results:")
        print(f"Total puzzles fetched: {len(valid_puzzles)}")
        print(f"Unique puzzle IDs: {len(unique_ids)}")
        
        return len(unique_ids) == len(valid_puzzles)

    def run_all_tests(self):
        """Run all anti-caching tests"""
        print("🚀 Starting Anti-Caching Tests")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Basic fetch
        puzzle_id = self.test_basic_fetch()
        results['basic_fetch'] = puzzle_id is not None
        
        # Test 2: Multiple fetches
        results['multiple_fetches'] = self.test_multiple_fetches(5)
        
        # Test 3: Different settings
        setting_results = self.test_different_settings()
        results['different_settings'] = len([r for r in setting_results if r is not None]) > 0
        
        # Test 4: Cache-busting parameters
        results['cache_busting'] = self.test_cache_busting_parameters()
        
        # Test 5: Difficulty cycling
        results['difficulty_cycling'] = self.test_difficulty_cycling()
        
        # Test 6: Color cycling
        results['color_cycling'] = self.test_color_cycling()
        
        # Test 7: Theme cycling
        results['theme_cycling'] = self.test_theme_cycling()
        
        # Test 8: Parameter variation
        results['parameter_variation'] = self.test_parameter_variation()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        total_passed = sum(results.values())
        total_tests = len(results)
        
        print(f"\nOverall: {total_passed}/{total_tests} tests passed")
        
        if total_passed == total_tests:
            print("🎉 All tests passed! Anti-caching strategies are working.")
        else:
            print("⚠️ Some tests failed. Check the implementation.")
        
        return results

def main():
    """Main function to run the tests"""
    tester = AntiCacheTester()
    results = tester.run_all_tests()
    return results

if __name__ == "__main__":
    main()
