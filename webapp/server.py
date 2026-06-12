"""FastAPI app: serves the static UI and drives the game over a WebSocket.

Phase 1: a single shared session -- one human seat (BLUE) versus three bots.
Clients identify themselves with a token (persisted in localStorage) so they can
reconnect to their seat. Extra clients become spectators until 'New Game'.
"""

import os
import secrets
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import gameboard
from .controllers import BotController, HumanController
from .session import GameSession

STATIC = Path(__file__).parent / "static"

# Pacing beat before each seat acts. Override with e.g. BLOKUS_TURN_DELAY=0.2
TURN_DELAY = float(os.environ.get("BLOKUS_TURN_DELAY", "0.6"))
# "phase1" = you (blue) vs 3 bots; "phase2" = you (blue+yellow) vs one bot (red+green)
MODE = os.environ.get("BLOKUS_MODE", "phase2")
ALL_BOTS = bool(os.environ.get("BLOKUS_ALL_BOTS"))

C = gameboard


def _bot(label="Bot"):
	return BotController(C.BlokusGreedyLookAheadPlayer(), label=label)


def _phase1():
	blue = _bot("Random bot") if ALL_BOTS else HumanController(label="You")
	controllers = {
		C.BLUE: blue,
		C.RED: BotController(C.BlokusGreedyLookAheadPlayer(), label="Lookahead bot"),
		C.YELLOW: BotController(C.BlokusGreedyPlayer(), label="Greedy bot"),
		C.GREEN: BotController(C.BlokusRandomPlayer(), label="Random bot"),
	}
	claim_groups = [] if ALL_BOTS else [[C.BLUE]]
	return GameSession(controllers, turn_delay=TURN_DELAY, claim_groups=claim_groups)


def _phase2():
	# You play the blue+yellow diagonal; one bot plays the red+green diagonal.
	mk_you = _bot if ALL_BOTS else (lambda: HumanController(label="You"))
	controllers = {
		C.BLUE: mk_you(), C.YELLOW: mk_you(),
		C.RED: _bot(), C.GREEN: _bot(),
	}
	claim_groups = [] if ALL_BOTS else [[C.BLUE, C.YELLOW]]
	teams = [
		{"label": "You", "colors": [C.BLUE, C.YELLOW]},
		{"label": "Bot", "colors": [C.RED, C.GREEN]},
	]
	return GameSession(controllers, turn_delay=TURN_DELAY, claim_groups=claim_groups, teams=teams)


def make_default_session():
	return _phase1() if MODE == "phase1" else _phase2()


class Hub:
	def __init__(self):
		self.connections = {}          # websocket -> token
		self.session = None
		self.set_session(make_default_session())

	def set_session(self, session):
		self.session = session
		session.broadcaster = self.broadcast

	async def broadcast(self):
		for ws, token in list(self.connections.items()):
			await self._safe_send(ws, self._state_message(token))

	async def send_state(self, ws, token):
		await self._safe_send(ws, self._state_message(token))

	def _state_message(self, token):
		msg = {"type": "state"}
		msg.update(self.session.public_state())
		msg.update(self.session.private_state(token))
		return msg

	async def _safe_send(self, ws, msg):
		try:
			await ws.send_json(msg)
		except Exception:
			self.connections.pop(ws, None)


hub = Hub()
app = FastAPI()
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


@app.get("/")
async def index():
	return FileResponse(str(STATIC / "index.html"))


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
	await ws.accept()
	try:
		while True:
			data = await ws.receive_json()
			await dispatch(ws, data)
	except WebSocketDisconnect:
		on_disconnect(ws)
	except Exception:
		on_disconnect(ws)


def on_disconnect(ws):
	token = hub.connections.pop(ws, None)
	# free the seat only when this was the token's last live connection
	if token and token not in hub.connections.values():
		hub.session.release_token(token)


async def dispatch(ws, data):
	mtype = data.get("type")
	session = hub.session

	if mtype == "join":
		token = data.get("token") or secrets.token_hex(8)
		hub.connections[ws] = token
		session.claim_seat(token, data.get("name"))
		await ws.send_json({"type": "welcome", "token": token})
		if not session.started:
			await session.advance()
		else:
			await hub.send_state(ws, token)

	elif mtype == "select_piece":
		token = hub.connections.get(ws)
		color = data.get("color")
		piece = data.get("piece")
		by_orientation = {}
		if (color in session.colors_owned_by(token)
				and session.status == "awaiting_human"
				and session.current_color == color):
			by_orientation = session.placements_for(color, piece)
		await ws.send_json({
			"type": "placements", "color": color, "piece": piece,
			"by_orientation": by_orientation,
		})

	elif mtype == "make_move":
		token = hub.connections.get(ws)
		ok, err = await session.handle_move(token, data.get("move_id"))
		if not ok:
			await ws.send_json({"type": "error", "message": err})

	elif mtype == "new_game":
		hub.set_session(make_default_session())
		for sock, token in hub.connections.items():
			hub.session.claim_seat(token)
		await hub.session.advance()
