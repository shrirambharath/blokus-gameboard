"""Seat controllers.

A Blokus game is always 4 seats (the 4 colors). Each seat is owned by a
controller -- either a bot (wrapping one of the engine strategies) or a human
(tied to a connected client by a token). A single controller may own more than
one seat (Phase 2: one human owns two diagonal colors; one bot owns the other
two). The GameSession only cares whether the seat-to-move is human or bot.
"""


class BotController:
	is_human = False

	def __init__(self, strategy, label=None):
		self.strategy = strategy
		self.label = label or strategy.player_type

	def assign_color(self, color_id, color):
		self.strategy.assign_color(color_id, color)

	def compute_move(self, board):
		# board has already been turned for this seat by the session
		return self.strategy.make_move(board)


class HumanController:
	is_human = True

	def __init__(self, label="human"):
		self.label = label
		self.token = None   # owning client token, None == unclaimed
		self.name = None

	def assign_color(self, color_id, color):
		self.color = color
		self.color_id = color_id
