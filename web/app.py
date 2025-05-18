from flask import Flask, render_template
from flask_socketio import SocketIO
from game.lichess_game import LichessVoiceGame, main
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
game_instance = None

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_game')
def handle_start_game():
    global game_instance
    game_instance = LichessVoiceGame()
    main(debug=False)
    return {'status': 'Game started'}

if __name__ == '__main__':
    socketio.run(app, debug=True)
