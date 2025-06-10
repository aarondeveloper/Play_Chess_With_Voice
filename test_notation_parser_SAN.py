"""
Test script for SAN Chess Notation Parser with Voice Input
This combines Deepgram voice recognition with SAN parsing and plays moves on a real chess board.
"""
import os
import chess
import chess.pgn
from game.deepgram_voice_recognition import DeepgramVoiceRecognizer, get_chess_move_from_voice
from game.chess_notation_parser_SAN import parse_chess_notation_san_to_uci

def display_board(board):
    """Display the current board position"""
    print("\n" + "="*50)
    print("CURRENT BOARD POSITION:")
    print("="*50)
    print(board)
    print("\nFEN:", board.fen())
    print("Move #", board.fullmove_number, "- White to move" if board.turn else "- Black to move")
    print("="*50)

def get_voice_move_with_audio_capture(board):
    """Get a chess move using proper audio capture (PyAudio → WAV → Deepgram → Text)"""
    print(f"\n🎙️ Say your move (Turn: {'White' if board.turn else 'Black'})...")
    print("Examples: 'pawn to e4', 'knight to f3', 'bishop takes c5', 'castle kingside'")
    input("Press Enter when ready to speak...")
    
    try:
        print("🎤 Starting audio capture pipeline...")
        
        # Step 1: Use working Deepgram voice capture (PyAudio → WAV file → Deepgram → Text)
        recognizer = DeepgramVoiceRecognizer()
        voice_text = recognizer.recognize_speech_simple()
        
        if not voice_text:
            print("❌ No speech detected by Deepgram")
            return None, None
        
        print(f"📝 Deepgram transcription: '{voice_text}'")
        
        # Check for special commands
        if any(cmd in voice_text.lower() for cmd in ['exit', 'quit', 'stop']):
            return "EXIT", None
        
        if "show board" in voice_text.lower():
            return "SHOW", None
        
        if "undo" in voice_text.lower() or "take back" in voice_text.lower():
            return "UNDO", None
        
        # Step 2: Convert voice text to SAN notation  
        from game.chess_notation_parser_SAN import parse_voice_to_san
        san_move = parse_voice_to_san(voice_text)
        
        if not san_move:
            print("❌ Could not convert voice text to SAN notation")
            return None, voice_text
        
        print(f"♟️ SAN notation: '{san_move}'")
        
        # Step 3: Convert SAN to UCI using python-chess
        from game.chess_notation_parser_SAN import convert_san_to_uci
        uci_move = convert_san_to_uci(san_move, board)
        
        if not uci_move:
            print("❌ Could not convert SAN to UCI (move may be illegal)")
            return None, voice_text
        
        print(f"🎯 UCI move: '{uci_move}'")
        print(f"✅ Complete pipeline: Audio → '{voice_text}' → '{san_move}' → '{uci_move}'")
        
        return uci_move, voice_text
            
    except Exception as e:
        print(f"❌ Error in voice processing pipeline: {e}")
        return None, None

def test_voice_chess_game():
    """Interactive chess game using voice input with SAN parsing"""
    print("🎙️♟️ Voice Chess Game with SAN Parser")
    print("="*60)
    
    # Check Deepgram credentials
    api_key = os.getenv('DEEPGRAM_API_KEY')
    if not api_key:
        print("❌ DEEPGRAM_API_KEY not found in environment variables")
        print("Please add your Deepgram API key to the .env file")
        return
    
    try:
        # Initialize components
        board = chess.Board()
        move_history = []
        
        print("✅ Chess board initialized")
        display_board(board)
        
        print("\n📝 INSTRUCTIONS:")
        print("- Say chess moves in natural language")
        print("- Examples: 'pawn to e4', 'knight to f3', 'queen takes d5'")
        print("- Special commands: 'exit', 'show board', 'undo'")
        print("- The game alternates between White and Black")
        print("- Audio pipeline: PyAudio → WAV file → Deepgram → Text → SAN → UCI")
        
        while True:
            try:
                # Get move from voice using complete audio capture pipeline
                uci_move, voice_text = get_voice_move_with_audio_capture(board)
                
                if uci_move == "EXIT":
                    print("👋 Exiting chess game...")
                    break
                elif uci_move == "SHOW":
                    display_board(board)
                    continue
                elif uci_move == "UNDO":
                    if move_history:
                        last_move = move_history.pop()
                        board.pop()
                        print(f"↩️ Undid move: {last_move}")
                        display_board(board)
                    else:
                        print("❌ No moves to undo")
                    continue
                elif not uci_move:
                    print("🔄 Try again...")
                    continue
                
                # Try to make the move
                try:
                    move = chess.Move.from_uci(uci_move)
                    
                    if move in board.legal_moves:
                        # Make the move
                        san_notation = board.san(move)
                        board.push(move)
                        move_history.append(f"{san_notation} ({uci_move})")
                        
                        print(f"✅ Move played: {san_notation}")
                        print(f"   Voice: '{voice_text}' → UCI: {uci_move}")
                        
                        display_board(board)
                        
                        # Check for game end
                        if board.is_checkmate():
                            winner = "Black" if board.turn else "White"
                            print(f"🏆 CHECKMATE! {winner} wins!")
                            break
                        elif board.is_stalemate():
                            print("🤝 STALEMATE! Game is a draw!")
                            break
                        elif board.is_check():
                            print("⚠️ CHECK!")
                        
                    else:
                        print(f"❌ Illegal move: {uci_move}")
                        print("   Legal moves:", [move.uci() for move in list(board.legal_moves)[:10]], "...")
                        
                except ValueError as e:
                    print(f"❌ Invalid UCI move format: {uci_move}")
                    print(f"   Error: {e}")
            
            except KeyboardInterrupt:
                print("\n⚠️ Game interrupted by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                continue
        
        # Show final game summary
        if move_history:
            print("\n📋 GAME SUMMARY:")
            print("-" * 30)
            for i, move in enumerate(move_history, 1):
                print(f"{i}. {move}")
        
    except Exception as e:
        print(f"❌ Failed to initialize voice chess game: {e}")

if __name__ == "__main__":
    print("🎙️♟️ SAN Chess Notation Parser with Voice Input")
    test_voice_chess_game() 