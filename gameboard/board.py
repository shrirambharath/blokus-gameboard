
import numpy as np
import gameboard 

"""	
	Blokus Board

	Setup: 
		B|R
		---
		G|Y

"""


class BoardStateException(Exception):
	"""
		Exception raised for errors in the state of the board
	"""
	def __init__(self, message):
		self.message = message


class BlokusBoard:
	def __init__(self, gridsize=20):
		self.gridsize = gridsize
		self._setup_players()
		self._setup_board()

	def _setup_players(self):
		self.players = { 
			gameboard.BLUE : { gameboard.ROTATION: 0, gameboard.COLOR: 1 },
			gameboard.RED : { gameboard.ROTATION: 1, gameboard.COLOR: 2 },
			gameboard.YELLOW : { gameboard.ROTATION: 2, gameboard.COLOR: 3 },
			gameboard.GREEN : { gameboard.ROTATION: 3, gameboard.COLOR: 4 }			
		 }

	def _setup_board(self):
		self.grid = [[0 for i in range(0,self.gridsize)] for i in range(0,self.gridsize)]

		all_pieces = [
			gameboard.BlokusPiece_I5(),
			gameboard.BlokusPiece_N(),
			gameboard.BlokusPiece_V5(),
			gameboard.BlokusPiece_T5(),
			gameboard.BlokusPiece_U(),
			gameboard.BlokusPiece_L5(),
			gameboard.BlokusPiece_Y(),
			gameboard.BlokusPiece_Z5(),
			gameboard.BlokusPiece_W(),
			gameboard.BlokusPiece_P(),
			gameboard.BlokusPiece_X(),
			gameboard.BlokusPiece_F(),
			gameboard.BlokusPiece_Z4(),
			gameboard.BlokusPiece_I4(),
			gameboard.BlokusPiece_L4(),
			gameboard.BlokusPiece_O(),
			gameboard.BlokusPiece_T4(),
			gameboard.BlokusPiece_I3(),
			gameboard.BlokusPiece_V3(),
			gameboard.BlokusPiece_2(),
			gameboard.BlokusPiece_1()
		]
		unplayed_pieces = { p.piece_name : p for p in all_pieces }

		self.pieces = {
			gameboard.BLUE: { gameboard.UNPLAYED: unplayed_pieces.copy(), gameboard.PLAYED: [] },
			gameboard.RED: { gameboard.UNPLAYED: unplayed_pieces.copy(), gameboard.PLAYED: [] },
			gameboard.YELLOW: { gameboard.UNPLAYED: unplayed_pieces.copy(), gameboard.PLAYED: [] },
			gameboard.GREEN: { gameboard.UNPLAYED: unplayed_pieces.copy(), gameboard.PLAYED: [] }
		}
		self.current_player = None


	def turn_board(self, player):
		if self.current_player is not None:
			raise BoardStateException('Board prepped for player: %s' % self.current_player)

		# rotate the board for the player
		self.current_player = player
		self._rotate_board(player)



	def return_board(self, player):
		if self.current_player != player:
			raise BoardStateException('Board prepped for player: %s. Player %s cannot return' % (self.current_player, player))
		self.current_player = player

		# rotate the board back to normal
		self._unrotate_board(player)
		self.current_player = None



	def play_piece(self, player, piece_name, piece_orientation_index, coord_i, coord_j):
		# verify that the player is valid and that is their turn
		if player not in self.pieces:
			raise BoardStateException('Unknown player: %s' % player)
		if player != self.current_player:
			raise BoardStateException('Board prepped for player: %s. Not %s turn' % (self.current_player, player))

		# verify that the piece name is valid & that the player hasn't played this piece before
		if piece_name in self.pieces[player][gameboard.PLAYED]:
			raise BoardStateException('Piece: %s has already been played' % piece_name)
		if piece_name not in self.pieces[player][gameboard.UNPLAYED]:
			raise BoardStateException('Unknown Piece: %s' % piece_name)

		# verify that the orientation index is valid for the piece
		if piece_orientation_index not in self.pieces[player][gameboard.UNPLAYED][piece_name].piece_grid_orientations:
			raise BoardStateException('Unknown orientation %d for piece %s' % (piece_orientation_index, piece_name))

		# retrieve the correct piece grid orientation
		piece_grid = self.pieces[player][gameboard.UNPLAYED][piece_name].piece_grid_orientations[piece_orientation_index]		
		is_valid_move, error_reason = self._validate_play_piece(player, piece_grid, coord_i, coord_j)
		if not is_valid_move:
			return False

		# place piece on board
		self._place_piece_on_board(player, piece_grid, coord_i, coord_j)

		# move piece from unplayed to played
		played_pieces = self.pieces[player][gameboard.PLAYED]
		played_pieces.append(self.pieces[player][gameboard.UNPLAYED].pop(piece_name))
		self.pieces[player][gameboard.PLAYED] = played_pieces

		return True


	def _rotate_board(self, player):
		rotation_index = self.players[player][gameboard.ROTATION]
		self.grid = np.rot90(self.grid, rotation_index)


	def _unrotate_board(self, player):
		rotation_index = self.players[player][gameboard.ROTATION]
		self.grid = np.rot90(self.grid, rotation_index * -1)


	def _validate_play_piece(self, player, piece_grid, coord_i, coord_j):
		# Assuming here that all the player & piece level info has been validated. No further validation is performed here
		# Validates the following in order - 
		#	0. 	if the first piece being played, if the coords are (0,0) AND piece_grid[0][0] is 1. Edge case for small boards, 
		# 		check to see if the piece is smaller than the board
		#		No other tests (1/2/3) need to be performed
		#
		#	Sequence of the next 3 checked is important. 
		#	1. 	does the piece fit? (all 1's on the piece grid should map to 0's on grid) / out of bounds?
		#	2. 	does it form contiguous blocks of same color
		#	3. 	does it contact a corner? (check outer 1's to see if it corners on the grid)
		
		# case 0
		if len(self.pieces[player][gameboard.PLAYED]) == 0: 
			#first move - HAS to go here first
			if coord_i == 0 and coord_j == 0 and \
				piece_grid[0][0] == 1 and \
				len(self.grid) >= len(piece_grid) and len(self.grid) >= len(piece_grid[0]):
				return True, gameboard.NOT_APPLICABLE
			else:
				return False, gameboard.INVALID_FIRST_MOVE

		# case 1 - does piece fit, if not return false
		for i in range(0, len(piece_grid)):
			for j in range(0, len(piece_grid[0])):
				if piece_grid[i][j] == 1:
					if (coord_i + i) >= self.gridsize or (coord_j + j) >= self.gridsize:
						#piece is going out of bounds of the board
						return False, gameboard.OUT_OF_GRID
					if self.grid[coord_i + i][coord_j + j] != 0:
				  		#spot on grid is already occurpied
						return False, gameboard.BLOCK_OCCUPIED

		connects_corner = False
		for i in range(0, len(piece_grid)):
			for j in range(0, len(piece_grid[0])):
				if piece_grid[i][j] == 1:
					# case 2 - does it form contiguous blocks of same color, if so return false
					if (coord_i + i - 1 >= 0 and self.grid[coord_i + i - 1][coord_j + j] == self.players[player][gameboard.COLOR]) or \
						(coord_i + i + 1 < len(self.grid) and self.grid[coord_i + i + 1][coord_j + j] == self.players[player][gameboard.COLOR] ) or \
						(coord_j + j - 1 >= 0 and self.grid[coord_i + i][coord_j + j - 1] == self.players[player][gameboard.COLOR]) or \
						(coord_j + j + 1 < len(self.grid) and self.grid[coord_i + i][coord_j + j + 1] == self.players[player][gameboard.COLOR]):
						return False, gameboard.CONTIGUOUS_BLOCKS

					# case 3 - does it contact at least one corner
					if not connects_corner:
						if coord_i + i - 1 >= 0:
							if coord_j + j - 1 >= 0:
								if self.grid[coord_i + i - 1][coord_j + j - 1] == self.players[player][gameboard.COLOR]:
									connects_corner = True
							if not connects_corner and coord_j + j + 1 < len(self.grid):
								if self.grid[coord_i + i - 1][coord_j + j + 1] == self.players[player][gameboard.COLOR]:	
									connects_corner = True
						if not connects_corner and coord_i + i + 1 < len(self.grid):
							if coord_j + j - 1 >= 0:
								if self.grid[coord_i + i + 1][coord_j + j - 1] == self.players[player][gameboard.COLOR]:
									connects_corner = True
							if not connects_corner and coord_j + j + 1 < len(self.grid):
								if self.grid[coord_i + i + 1][coord_j + j + 1] == self.players[player][gameboard.COLOR]:	
									connects_corner = True

		# safe because if it had hit a corner early, but later found to be hitting contiguous blocks, the funtion would return false
		if connects_corner:
			return True, gameboard.NOT_APPLICABLE
		else:
			return False, gameboard.NO_CORNER



	def _place_piece_on_board(self, player, piece_grid, coord_i, coord_j):
		# Assuming here that all the validation has been complete. No further validation is performed here
		for i in range(0, len(piece_grid)):
			for j in range(0, len(piece_grid[0])):
				if piece_grid[i][j] == 1:
					self.grid[coord_i + i][coord_j + j] = self.players[player][gameboard.COLOR]


	def validate_play_piece_helper(self, player, piece_grid, coord_i, coord_j):
		is_valid_move, error_reason = self._validate_play_piece(player, piece_grid, coord_i, coord_j) 
		return is_valid_move


	def pretty_print(self):
		for i in range(0, self.gridsize):
			line = []
			for j in range(0, self.gridsize):
				x = self.grid[i][j]
				if x == 0:
					line += ['.']
				else:
					line += [str(x)]
			print(''.join(line))
		print('\n\n')

