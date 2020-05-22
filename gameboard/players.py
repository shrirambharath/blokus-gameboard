import gameboard 
import random

class BlokusRandomPlayer:
	def __init__(self):
		self.player_type = gameboard.RANDOM_PLAYER

	def assign_color(self, color):
		self.color = color
		self.player_name = "%s-%s" % (self.color, self.player_type)
		if self.color not in [gameboard.BLUE, gameboard.RED, gameboard.GREEN, gameboard.YELLOW]:
			raise BoardStateException("Unknown color: %s" % self.color)

	def make_move(self, board):			
		return self._make_random_move(board)


	def _make_random_move(self, board):
		_grid = board.grid
		_unplayed_pieces = board.pieces[self.color][gameboard.UNPLAYED]
		_color_id = board.players[self.color][gameboard.COLOR]

		_i_j_candidates = self._identify_i_j_candidates(_color_id, _grid, board.gridsize)
		
		_candidate_tuples = []
		for (i,j) in _i_j_candidates:
			for (piece_name, piece) in _unplayed_pieces.items():
				for (piece_orientation_index, piece_grid) in piece.piece_grid_orientations.items():
					if board.validate_play_piece_helper(self.color, piece_grid, i, j):
						_candidate_tuples += [[piece_name, piece_orientation_index, i, j]]

		if len(_candidate_tuples) > 0:
			# return piece_name, piece_orientation_index, coord_i, coord_j
			return random.choice(_candidate_tuples)
		else:
			return [None, -1, -1, -1]


	def _identify_i_j_candidates(self, color_id, grid, gridsize):
		if (grid[0][0] == 0):
			return [(0,0)]
		
		_candidates = []
		for i in range(0,gridsize):
			for j in range(0,gridsize-1):
				if grid[i][j] == color_id and grid[i][j+1] != color_id:
					if i-1 >= 0 and grid[i-1][j+1] == 0:
						_candidates += [(i-1,j+1)]
					if i+1 < gridsize and grid[i+1][j+1] == 0:
						_candidates += [(i+1,j+1)]
		return _candidates


