# Voice-Controlled Chess

A voice-controlled chess application that allows you to play on Lichess.org using voice commands.

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install berserk python-chess pyttsx3 SpeechRecognition pyaudio python-dotenv
   ```
3. Create a `.env` file in the project root with your Lichess API token:
   ```
   LICHESS_API_TOKEN=your_token_here
   ```
4. Run the test scripts to verify your setup:
   ```
   python test_lichess_connection.py
   python test_voice_recognition.py
   ```
5. Run the main application:
   ```
   python sample_structure.py
   ```

## How to Get a Lichess API Token

1. Create a Lichess account if you don't have one
2. Go to https://lichess.org/account/oauth/token
3. Create a new personal token with the `board:play` scope

## Usage

- Say chess moves in standard notation (e.g., "e2 to e4", "Knight to f3")
- The application will make the move on Lichess and announce your opponent's moves

## Features

- Voice control for chess moves
- Real-time game streaming
- Support for human opponents 