"""FastAPI app: serves the static UI and drives the game over a WebSocket.

Phase 1: a single shared session -- one human seat (BLUE) versus three bots.
Clients identify themselves with a token (persisted in localStorage) so they can
reconnect to their seat. Extra clients become spectators until 'New Game'.
"""

import secrets
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import gameboard
from .controllers import BotController, HumanController
from .session import GameSession

STATIC = Path(__file__).parent / "static"


def make_default_session():
	controllers = {
		gameboard.BLUE: HumanController(label="You"),
		gameboard.RED: BotController(gameboard.BlokusGreedyLookAheadPlayer(), label="Lookahead bot"),
		gameboard.YELLOW: BotController(gameboard.BlokusGreedyPlayer(), label="Greedy bot"),
		gameboard.GREEN: BotController(gameboard.BlokusRandomPlayer(), label="Random bot"),
	}
	return GameSession(controllers)


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
		hub.connections.pop(ws, None)
	except Exception:
		hub.connections.pop(ws, None)


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
