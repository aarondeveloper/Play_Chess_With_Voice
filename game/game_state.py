"""Module for managing chess game state"""

class GameState:
    def __init__(self):
        self.my_color = None
        self.current_moves = []
        self.is_my_turn = False
        self.game_id = None
        self.status = None
        
    def set_color(self, color):
        """Set player color and initial turn"""
        self.my_color = color
        # If we're white, it's our turn first
        self.is_my_turn = (color == 'white')
        print(f"Playing as {color} - {'your' if self.is_my_turn else 'opponent'}'s turn first")

    def update_from_event(self, event):
        """Update state from a game event"""
        if event['type'] == 'gameState':
            # Debug print the entire event
            print(f"DEBUG Event: {event}")
            
            self.status = event.get('status')
            old_turn = self.is_my_turn
            
            # Determine turn based on moves and our color
            moves = event.get('moves', '').split()
            num_moves = len(moves)
            # It's our turn if:
            # - We're white and moves count is even (0, 2, 4...)
            # - We're black and moves count is odd (1, 3, 5...)
            self.is_my_turn = (num_moves % 2 == 0) == (self.my_color == 'white')
            
            print(f"DEBUG Turn changed: {old_turn} -> {self.is_my_turn}")
            print(f"DEBUG Moves count: {num_moves}, Our color: {self.my_color}")
            
            # Update moves
            if moves:
                if len(moves) > len(self.current_moves):
                    last_move = moves[-1]
                    # Don't report our own move as opponent's move
                    if len(self.current_moves) == len(moves) - 1:
                        # This is a new move
                        is_opponent_move = not self.is_my_turn  # If it's our turn, last move was opponent's
                        self.current_moves = moves
                        if is_opponent_move:
                            print(f"DEBUG: Opponent moved, our turn: {self.is_my_turn}")
                            return last_move
            
            # Print more info for debugging
            print(f"Turn: {'ours' if self.is_my_turn else 'opponents'}")
            if self.current_moves:
                print(f"Current moves: {' '.join(self.current_moves)}")
        
        return None 