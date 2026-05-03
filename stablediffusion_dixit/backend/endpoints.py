from multiprocessing import freeze_support
from pathlib import Path

from flask import Flask, request, send_from_directory, send_file
from flask_socketio import SocketIO, emit
from stablediffusion_dixit.game_logic.player import Player

from stablediffusion_dixit.game_logic.model import GameState, GamePhase

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIST = BASE_DIR / "hackharvard_frontend" / "dist"

app = Flask(__name__)
app.config["SECRET_KEY"] = "key"
socketio = SocketIO(app, cors_allowed_origins='*')



@app.route("/", methods=["GET"])
def main():
    return send_file(FRONTEND_DIST / "index.html")

@app.route("/assets/<path:path>")
def mainpath(path):
    return send_from_directory(FRONTEND_DIST / "assets", path)

@app.route("/blah", methods=["POST"])
def blah():
    req = request.get_json()
    return {
        "resp": f"Hello, {req['name']}"
    }

@app.route("/images/<path:path>")
def serve_image(path):
    return send_from_directory(BASE_DIR / "images", path)

@app.route("/animations/<path:path>")
def serve_anim(path):
    return send_from_directory(BASE_DIR / "animations", path)

@app.route("/premade_animations/<path:path>")
def serve_premade_anim(path):
    print(path)
    return send_from_directory(BASE_DIR / "premade_animations", path)

@socketio.on("join_game")
def join_game(data):
    game_state.add_player(Player(request.sid,data['name']))


@socketio.on("join_tv")
def join_tv(data):
    print("joined tv")
    game_state.add_tv(request.sid)

@socketio.on("enter_prompt")
def enter_prompt(data):
    prompt_text = data["prompt"]
    game_state.receive_prompt(request.sid,prompt_text)
    

@socketio.on("start_game")
def start_game(data):
    game_state.start_game()

@socketio.on("active_player_proceed")
def proceed(data):
    game_state.receive_proceed_active_player(request.sid)

@socketio.on("vote")
def vote(data):
    game_state.receive_vote(request.sid,int(data['vote']))

@socketio.on("connect")
def connect():
    print(request.sid)

@socketio.on("disconnect")
def disconnect(reason=None):
    game_state.remove_sid(request.sid)


if __name__ == "__main__":
    freeze_support()
    game_state = GameState(app, socketio)
    socketio.run(app, debug=False, host='0.0.0.0', port = 5001)
