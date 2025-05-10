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

    def update_from_event(self, event):
        """Update state from a game event"""
        if event['type'] == 'gameState':
            # Update game status
            old_status = self.status
            self.status = event.get('status')
            
            # Check for game end conditions
            if self.status == 'mate':
                return 'checkmate', event.get('winner')
            elif self.status == 'resign':
                return 'resign', event.get('winner')
            elif self.status == 'draw':
                return 'draw', None
            
            # Rest of the existing move processing code...
            old_turn = self.is_my_turn
            
            # Determine turn based on moves and our color
            moves = event.get('moves', '').split() if event.get('moves') else []
            num_moves = len(moves)
            self.is_my_turn = (num_moves % 2 == 0) == (self.my_color == 'white')
            
            # Update moves and board state
            if moves:  # Only process if there are actual moves
                if len(moves) > len(self.current_moves):
                    last_move = moves[-1]
                    # Don't report our own move as opponent's move
                    if len(self.current_moves) == len(moves) - 1:
                        is_opponent_move = not self.is_my_turn
                        
                        # Only convert and return if it's opponent's move
                        if not is_opponent_move:
                            # Convert UCI to SAN before updating board
                            san_move = self.get_san_move(last_move)
                            # Update board with UCI move
                            self.board.push_uci(last_move)
                            self.current_moves = moves
                            return last_move, san_move
                        else:
                            # Just update board and moves for our moves
                            self.board.push_uci(last_move)
                            self.current_moves = moves
            
            # Print more info for debugging
            print(f"Turn: {'ours' if self.is_my_turn else 'opponents'}")
            if self.current_moves:
                print(f"Current moves: {' '.join(self.current_moves)}")
        
        return None, None 