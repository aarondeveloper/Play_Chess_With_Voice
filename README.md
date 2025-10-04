# Play Chess With Voice

A Python application that allows you to play chess on Lichess using voice commands. This project enables hands-free chess gameplay by converting your spoken moves into chess notation and executing them on the board.

## Requirements

- Python 3.11 (required for system parity)
- A Lichess account
- A Deepgram account (free tier available)
- A microphone
- Speakers or headphones

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/Play_Chess_With_Voice.git
cd Play_Chess_With_Voice
```

2. Create a virtual environment (recommended):
```bash
python3.11 -m venv play_chess_voice
source play_chess_voice/bin/activate  # On Windows: play_chess_voice\Scripts\activate
```

3. Install the required packages:
```bash
pip3.11 install -r requirements.txt
```

**⚠️ IMPORTANT: Deepgram SDK Version**
This project requires Deepgram SDK v3.2.7 (older version) because the newer v5.0.0+ has breaking API changes.

If you encounter import errors with `PrerecordedOptions` or `FileSource`, run:
```bash
pip uninstall deepgram-sdk -y
pip install deepgram-sdk==3.2.7
```

4. Set up your API keys:

   a. Lichess API token:
   - Go to https://lichess.org/account/oauth/token
   - Create a new token with the following scopes:
     - `challenge:write`
     - `board:play`
   - Copy the token and save it securely

   b. Deepgram API key:
   - Go to https://console.deepgram.com/signup
   - Create a free account
   - Once logged in, go to the API keys section
   - Create a new API key
   - Copy the key and save it securely

5. Create a `.env` file in the project root with your API keys and opponent settings:
```bash
LICHESS_API_TOKEN=your_lichess_token_here
DEEPGRAM_API_KEY=your_deepgram_key_here
OPPONENT_USERNAME=username_to_challenge  # Optional: Set this to challenge specific opponents
```

## Game Setup

When you start a game, you'll be prompted to specify your game settings:

1. Time Control:
   - Choose between different time controls (e.g., 5+0, 10+0, 15+10)
   - Specify increment if desired

2. Challenge Type:
   - Open Challenge: Creates a public challenge that anyone can accept
   - Direct Challenge: Challenges a specific opponent (requires OPPONENT_USERNAME in .env)

3. Color Preference:
   - Choose your preferred color (white/black/random)

4. Game Type:
   - Rated: Game will affect your Lichess rating
   - Unrated: Game won't affect your rating

The system will then create the challenge and wait for your opponent to accept.

## Usage

1. Start the application:
```bash
python main.py
```

2. Voice Commands:

   ### Basic Moves
   - Simple pawn moves: "e4", "d5"
   - Piece moves: "knight to f3", "bishop to e4"
   - You can also say: "move knight to f3", "move bishop to e4"

   ### Captures
   - Pawn captures: "pawn from e takes g5", "e pawn takes g5", "e takes g5"
   - Piece captures: "knight takes e4", "bishop takes d5"

   ### Special Moves
   - Castling:
     - "castle kingside" or "castle short"
     - "castle queenside" or "castle long"
   - Pawn promotion:
     - "e8 queen" (promotes to queen)
     - "e8 knight" (promotes to knight)
     - "e8 bishop" (promotes to bishop)
     - "e8 rook" (promotes to rook)
     - "pawn from e takes d8 queen"
   - En passant:
     - "pawn from e takes d6" or "e pawn takes d6" or "e takes d6"

   Note: You don't need to say "check" when making a move - the system will automatically announce when you or your opponent is in check. Saying check can actually mess up my regex logic 

   ### Game Commands
   - "resign" - Resign the current game
   - "draw" - Offer a draw
   - "accept draw" - Accept a draw offer
   - "decline draw" - Decline a draw offer
   - "exit" - Exit the game

3. The system will:
   - Announce opponent's moves
   - Confirm your moves
   - Notify you of game status changes
   - Alert you if it doesn't understand your move

## Features

- Real-time voice recognition for chess moves using Deepgram's advanced speech-to-text
- Text-to-speech feedback for game events
- Support for all standard chess moves and special moves (castling, en passant)
- Game status announcements
- Draw offer handling
- Resignation capability
- Flexible game setup with time controls and challenge options

## Troubleshooting

If you encounter issues:

1. **Deepgram Import Errors**: If you get `ImportError: cannot import name 'PrerecordedOptions'`:
   ```bash
   pip uninstall deepgram-sdk -y
   pip install deepgram-sdk==3.2.7
   ```

2. **API Method Errors**: If you get `'Listen' object has no attribute 'rest'`:
   - This means you have the wrong Deepgram SDK version
   - Install the older version: `pip install deepgram-sdk==3.2.7`

3. Make sure your microphone is properly connected and configured
4. Check that your Lichess API token is valid
5. Verify your Deepgram API key is correct and has available credits
6. Ensure you're using Python 3.11
7. Verify all required packages are installed
8. Check your internet connection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Lichess API for providing the chess platform
- Deepgram for high-quality speech recognition
- Google Text-to-Speech for voice synthesis
