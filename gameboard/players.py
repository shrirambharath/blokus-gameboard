import gameboard 
import random


class BlokusPlayer:
	def __init__(self, player_type):
		self.player_type = player_type

	def assign_color(self, color_id, color):
		self.color = color
		self.color_id = color_id
		self.player_name = "%s-%s-%d" % (self.color, self.player_type, self.color_id)
		if self.color not in [gameboard.BLUE, gameboard.RED, gameboard.GREEN, gameboard.YELLOW]:
			raise BoardStateException("Unknown color: %s" % self.color)

	def __str__(self):
		return self.player_name

	def _identify_i_j_moves(self, board, _i_j_candidates, _unplayed_pieces):
		_candidate_tuples = []
		for (i,j) in _i_j_candidates:
			for (piece_name, piece) in _unplayed_pieces.items():
				for (piece_orientation_index, piece_grid) in piece.piece_grid_orientations.items():
					if board.validate_play_piece_helper(self.color, piece_grid, i, j):
						_candidate_tuples += [(piece, piece_orientation_index, i, j)]
		return _candidate_tuples



class BlokusRandomPlayer(BlokusPlayer):
	def __init__(self):
		super(BlokusRandomPlayer, self).__init__(gameboard.RANDOM_PLAYER)

	def make_move(self, board):			
		_grid = board.grid
		_unplayed_pieces = board.pieces[self.color][gameboard.UNPLAYED]
		_played_pieces = board.pieces[self.color][gameboard.PLAYED]
		_color_id = board.players[self.color][gameboard.COLOR]

		if len(_played_pieces) == 0:
			#no played pieces
			_i_j_candidates = [(0,0)]
		else:
			_all_candidates = gameboard.BlokusPlayerHelper.identify_corners(_grid, _color_id)
			_i_j_candidates = _all_candidates[_color_id]

		_candidate_tuples = self._identify_i_j_moves(board, _i_j_candidates, _unplayed_pieces)

		if len(_candidate_tuples) == 0:
			return (None, -1, -1, -1)

		# return piece, piece_orientation_index, coord_i, coord_j
		return random.choice(_candidate_tuples)



class BlokusGreedyPlayer(BlokusPlayer):
	def __init__(self):
		super(BlokusGreedyPlayer, self).__init__(gameboard.GREEDY_PLAYER)

	def make_move(self, board):			
		_grid = board.grid
		_unplayed_pieces = board.pieces[self.color][gameboard.UNPLAYED]
		_played_pieces = board.pieces[self.color][gameboard.PLAYED]
		_color_id = board.players[self.color][gameboard.COLOR]

		if len(_played_pieces) == 0:
			#no played pieces
			_i_j_candidates = [(0,0)]
		else:
			_all_candidates = gameboard.BlokusPlayerHelper.identify_corners(_grid, _color_id)
			_i_j_candidates = _all_candidates[_color_id]

		_candidate_tuples = self._identify_i_j_moves(board, _i_j_candidates, _unplayed_pieces)

		if len(_candidate_tuples) == 0:
			return (None, -1, -1, -1)

		# return piece, piece_orientation_index, coord_i, coord_j
		_candidate_tuples.sort(key=lambda x:x[0].block_count)

		# find all the pieces with the selected block count and randomly pick one
		_max_block_count = _candidate_tuples[-1][0].block_count
		_max_count_candidates = [x for x in _candidate_tuples if x[0].block_count == _max_block_count]

		return random.choice(_max_count_candidates)




class BlokusGreedyLookAheadPlayer(BlokusPlayer):
	def __init__(self):
		super(BlokusGreedyLookAheadPlayer, self).__init__(gameboard.GREEDY_LOOKAHEAD_PLAYER)


	def make_move(self, board):			
		_grid = board.grid
		_unplayed_pieces = board.pieces[self.color][gameboard.UNPLAYED]
		_played_pieces = board.pieces[self.color][gameboard.PLAYED]
		_color_id = board.players[self.color][gameboard.COLOR]

		if len(_played_pieces) == 0:
			#no played pieces
			_i_j_candidates = [(0,0)]
		else:
			_all_candidates = gameboard.BlokusPlayerHelper.identify_corners(_grid, _color_id)
			_i_j_candidates = _all_candidates[_color_id]

		_candidate_tuples = self._identify_i_j_moves(board, _i_j_candidates, _unplayed_pieces)

		# no moves found
		if len(_candidate_tuples) == 0:
			return (None, -1, -1, -1)

		#sort the candidates and filter out candidates with fewer than the max block count
		_candidate_tuples.sort(key=lambda x:x[0].block_count)
		_max_block_count = _candidate_tuples[-1][0].block_count
		_max_blockcount_candidate_tuples = [x for x in _candidate_tuples if x[0].block_count == _max_block_count]

		# for each candidate tuple calculate the corner differential and add to the sort factor
		# pick the best
		_final_candidate_tuples = []
		for (piece, piece_orientation_index, coord_i, coord_j) in _max_blockcount_candidate_tuples:
			_temp_grid = _grid.copy()
			piece_grid = piece.piece_grid_orientations[piece_orientation_index]

			for i in range(0, len(piece_grid)):
				for j in range(0, len(piece_grid[0])):
					if piece_grid[i][j] == 1:
						_temp_grid[coord_i + i][coord_j + j] = _color_id

			# do not update the lookahead skip tracker
			_temp_all_candidates = gameboard.BlokusPlayerHelper.identify_corners(_temp_grid, _color_id, False)

			# calculate how playing this piece changes the corner count
			differential = (3 * len(_temp_all_candidates[_color_id])) - sum([len(_temp_all_candidates[x]) for x in _temp_all_candidates.keys() if x != _color_id])

			_final_candidate_tuples += [(piece, piece_orientation_index, coord_i, coord_j, differential)]


		_final_candidate_tuples.sort(key=lambda x:x[4])

		# find all the pieces with the max differential and block count and randomly pick one
		_max_differential = _final_candidate_tuples[-1][4]
		_max_candidates = [x for x in _final_candidate_tuples if x[4] == _max_differential]

		# return piece, piece_orientation_index, coord_i, coord_j
		(piece, piece_orientation_index, coord_i, coord_j, _) = random.choice(_max_candidates)

		return (piece, piece_orientation_index, coord_i, coord_j)


