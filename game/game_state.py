"""Module for managing chess game state"""

class GameState:
    def __init__(self):
        self.my_color = None
        self.current_moves = []
        self.is_my_turn = False
        self.game_id = None
        self.status = None
        
    def update_from_event(self, event):
        """Update state from a game event"""
        if event['type'] == 'gameState':
            # The moves and status are directly in the event, not in a 'state' key
            self.status = event.get('status')
            self.is_my_turn = event.get('isMyTurn', False)
            
            # Update moves
            if 'moves' in event and event['moves']:
                new_moves = event['moves'].split()
                if len(new_moves) > len(self.current_moves):
                    last_move = new_moves[-1]
                    self.current_moves = new_moves
                    return last_move
            
            # Print more info for debugging
            print(f"Turn: {'ours' if self.is_my_turn else 'opponents'}")
            if self.current_moves:
                print(f"Current moves: {' '.join(self.current_moves)}")
        
        return None 