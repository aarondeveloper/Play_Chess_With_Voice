"""Module for managing chess game state"""
import chess

class GameState:
    def __init__(self):
        self.my_color = None
        self.current_moves = []
        self.is_my_turn = False
        self.game_id = None
        self.status = None
        self.board = None  # Will be initialized when game starts
        
    def set_color(self, color):
        """Set player color and initial turn"""
        self.my_color = color
        self.is_my_turn = (color == 'white')
        # Initialize fresh board when game starts
        self.board = chess.Board()
        print(f"Playing as {color} - {'your' if self.is_my_turn else 'opponent'}'s turn first")

    def get_san_move(self, uci_move):
        """Convert UCI move to algebraic notation"""
        move = chess.Move.from_uci(uci_move)
        san_move = self.board.san(move)
        return san_move

    def check_game_end(self, event):
        """Check if the game has ended"""
        if self.status == 'mate':
            return 'checkmate', event.get('winner')
        elif self.status == 'resign':
            return 'resign', event.get('winner')
        elif self.status == 'draw':
            return 'draw', None
        return None

    def update_from_event(self, event):
        """Update state from a game event"""
        if event['type'] == 'gameState':
            old_turn = self.is_my_turn
            
            # Determine turn based on moves and our color
            moves = event.get('moves', '').split() if event.get('moves') else []
            num_moves = len(moves)
            self.is_my_turn = (num_moves % 2 == 0) == (self.my_color == 'white')
            
            # Update moves and board state
            #if moves:  # Only process if there are actual moves
                # Special case: First move when we're black
            if len(self.current_moves) == 0 and self.my_color == 'black':
                last_move = moves[-1]
                san_move = self.get_san_move(last_move)
                self.board.push_uci(last_move)
                self.current_moves = moves
                move_info = (last_move, san_move)
            
            elif len(moves) > len(self.current_moves):
                last_move = moves[-1]
                # Don't report our own move as opponent's move
                if len(self.current_moves) == len(moves) - 1:
                    is_opponent_move = not self.is_my_turn
                    
                    # Process move regardless of whose it is
                    san_move = self.get_san_move(last_move)
                    self.board.push_uci(last_move)
                    self.current_moves = moves
                    
                    # Only return move info for opponent moves
                    move_info = (last_move, san_move) if not is_opponent_move else None
            
            # Update game status and check for end conditions
            self.status = event.get('status')
            print(f"the event {event}")
            print(f"Game status: {self.status}")
            game_end = self.check_game_end(event)
            if game_end:
                return game_end
            
            return move_info
        
        # Print more info for debugging
        print(f"Turn: {'ours' if self.is_my_turn else 'opponents'}")
        if self.current_moves:
            print(f"Current moves: {' '.join(self.current_moves)}")
        
        return None, None
        
        return None, None 