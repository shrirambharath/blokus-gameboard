"""Event-driven game session.

Unlike BlokusGame (a blocking pull-loop used by the CLI sims), GameSession is a
state machine: it rolls through bot seats inline, pauses at a human seat, and
resumes when that human's move arrives over the network. The server is
authoritative for all rules -- a submitted move_id is re-validated by the engine.
"""

import asyncio
import random

import numpy as np
import gameboard
from gameboard import BLUE, RED, YELLOW, GREEN, COLOR, ROTATION, UNPLAYED, PLAYED

from . import moves

SEAT_COLORS = [BLUE, RED, YELLOW, GREEN]


class GameSession:
	def __init__(self, controllers, bot_delay=0.4, start_index=None):
		# controllers: dict color -> BotController | HumanController
		self.board = gameboard.BlokusBoard(20)
		self.controllers = controllers
		self.bot_delay = bot_delay

		for color in SEAT_COLORS:
			controllers[color].assign_color(self.board.players[color][COLOR], color)

		self.turn_order = SEAT_COLORS[:]
		self.start_index = start_index if start_index is not None else random.randint(0, 3)
		self.idx = self.start_index
		self.done = set()
		self.status = "idle"          # idle | awaiting_human | bot_thinking | game_over
		self.current_color = None
		self.final_scores = {}
		self.started = False
		self.broadcaster = None       # async callable, injected by the server
		self.lock = asyncio.Lock()

	# ---- seat ownership ----------------------------------------------------

	def human_colors(self):
		return [c for c in SEAT_COLORS if self.controllers[c].is_human]

	def colors_owned_by(self, token):
		return [c for c in self.human_colors() if self.controllers[c].token == token]

	def claim_seat(self, token, name=None):
		"""Claim a free human seat for this token; returns the colors owned.

		Re-claiming with a known token returns the already-owned seats (reconnect).
		Returns [] when every human seat is taken (the client is a spectator).
		"""
		owned = self.colors_owned_by(token)
		if owned:
			return owned
		for color in self.human_colors():
			if self.controllers[color].token is None:
				self.controllers[color].token = token
				self.controllers[color].name = name
				return [color]
		return []

	# ---- turn flow ---------------------------------------------------------

	async def advance(self):
		async with self.lock:
			await self._advance_locked()

	async def _advance_locked(self):
		self.started = True
		while len(self.done) < len(SEAT_COLORS):
			color = self.turn_order[self.idx]
			self.idx = (self.idx + 1) % len(SEAT_COLORS)
			if color in self.done:
				continue

			if self.controllers[color].is_human:
				if not self._human_has_move(color):
					self.done.add(color)   # auto-pass a stuck human
					continue
				self.current_color = color
				self.status = "awaiting_human"
				await self._broadcast()
				return

			# bot seat: compute + apply inline, with a small delay to animate
			self.current_color = color
			self.status = "bot_thinking"
			if not self._bot_move(color):
				self.done.add(color)
			await self._broadcast()
			await asyncio.sleep(self.bot_delay)

		self.status = "game_over"
		self.current_color = None
		self._finalize()
		await self._broadcast()

	async def handle_move(self, token, move_id):
		"""Apply a human move (by move_id), then advance through the bots."""
		async with self.lock:
			if self.status != "awaiting_human":
				return False, "no move is awaited right now"
			color = self.current_color
			if color not in self.colors_owned_by(token):
				return False, "it is not your turn"
			try:
				piece_name, o_index, ci, cj = self._parse_move_id(move_id)
			except Exception:
				return False, "malformed move"
			if not self._apply_human_move(color, piece_name, o_index, ci, cj):
				return False, "illegal move"
			await self._broadcast()
			await self._advance_locked()
		return True, None

	# ---- engine glue (each does a single turn_board/return_board) -----------

	def _bot_move(self, color):
		self.board.turn_board(color)
		try:
			piece, o_index, ci, cj = self.controllers[color].compute_move(self.board)
			if piece is None:
				return False
			self.board.play_piece(color, piece.piece_name, o_index, ci, cj)
			return True
		finally:
			self.board.return_board(color)

	def _apply_human_move(self, color, piece_name, o_index, ci, cj):
		self.board.turn_board(color)
		try:
			return self.board.play_piece(color, piece_name, o_index, ci, cj)
		finally:
			self.board.return_board(color)

	def _human_has_move(self, color):
		self.board.turn_board(color)
		try:
			return moves.has_any_move(self.board, color)
		finally:
			self.board.return_board(color)

	def placements_for(self, color, piece_name):
		"""Legal placements for a picked piece (global coords), for the UI."""
		self.board.turn_board(color)
		try:
			return moves.enumerate_placements(self.board, color, piece_name)
		finally:
			self.board.return_board(color)

	def _parse_move_id(self, move_id):
		name, o_index, ci, cj = move_id.rsplit(":", 3)
		return name, int(o_index), int(ci), int(cj)

	# ---- scoring -----------------------------------------------------------

	def _score(self, color):
		pts = [p.block_count for p in self.board.pieces[color][PLAYED]]
		bonus = 0
		if len(pts) == 21:                 # all pieces placed
			bonus = 20 if pts[-1] == 1 else 15
		return sum(pts) + bonus

	def _finalize(self):
		self.final_scores = {color: self._score(color) for color in SEAT_COLORS}

	# ---- serialization for the client --------------------------------------

	async def _broadcast(self):
		if self.broadcaster:
			await self.broadcaster()

	def public_state(self):
		seats = []
		for color in SEAT_COLORS:
			ctrl = self.controllers[color]
			seats.append({
				"color": color,
				"color_id": self.board.players[color][COLOR],
				"is_human": ctrl.is_human,
				"label": getattr(ctrl, "label", ""),
				"name": getattr(ctrl, "name", None),
				"done": color in self.done,
				"pieces_left": len(self.board.pieces[color][UNPLAYED]),
				"score": self._score(color),
			})
		return {
			"grid": np.asarray(self.board.grid).tolist(),
			"seats": seats,
			"current_color": self.current_color,
			"status": self.status,
			"start_color": self.turn_order[self.start_index],
			"final_scores": self.final_scores if self.status == "game_over" else None,
		}

	def private_state(self, token):
		my_colors = self.colors_owned_by(token)
		your_turn = self.status == "awaiting_human" and self.current_color in my_colors
		pieces = {}
		for color in my_colors:
			rotation = self.board.players[color][ROTATION]
			plist = [{
				"name": name,
				"block_count": piece.block_count,
				"orientations": moves.piece_orientations_global(piece, rotation),
			} for name, piece in self.board.pieces[color][UNPLAYED].items()]
			plist.sort(key=lambda p: (-p["block_count"], p["name"]))
			pieces[color] = plist
		return {
			"your_colors": my_colors,
			"your_turn": your_turn,
			"your_pieces": pieces,
		}
