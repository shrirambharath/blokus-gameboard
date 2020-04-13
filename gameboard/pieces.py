
import numpy as np

class BlokusPiece:
	"""
		Blokus piece is an abstract class that extends to all other pieces
		Every piece has a nem (https://c2strategy.files.wordpress.com/2011/04/piecenamesall.png)
		Its basic structire is represented in a 2-d grid, but to actually reference in on the board
		retrieve it from the piece_gris_orientations map. The index of the map is an orientation id 
		and the value is the 2-d map orientation of the specific piece.
		The block count can be used to lookup the size of the block
	"""
	def __init__(self, piece_name, piece_grid):
		self.piece_name = piece_name
		self.piece_grid = np.array(piece_grid, int)
		self.block_count = self._count_blocks(piece_grid)
		self.piece_grid_orientations = self._generate_orientations()

	def _generate_orientations(self):
		_seen_orientations = set()
		_orientations = { }

		# rotate array by 90 deg 4 times
		_index = 0
		for rotate_index in range(0,4):
			_next_orientation = np.rot90(self.piece_grid, rotate_index)
			_rep = BlokusPiece.representation(_next_orientation)
			if _rep not in _seen_orientations:
				_seen_orientations.add(_rep)
				_orientations[_index] = _next_orientation
				_index += 1

		# mirror the piece & rotate 4 times
		_next_orientation = np.flip(self.piece_grid, axis=0)
		for rotate_index in range(0,4):
			_next_orientation = np.rot90(_next_orientation, rotate_index)
			_rep = BlokusPiece.representation(_next_orientation)
			if _rep not in _seen_orientations:
				_seen_orientations.add(_rep)
				_orientations[_index] = _next_orientation
				_index += 1

		return _orientations

	def _count_blocks(self, grid):
		return sum([sum(grid[i]) for i in range(0,len(grid))])

	def representation(piece):
		op = '\n'.join([''.join([str(piece[i][j]) for j in range(0, len(piece[i]))]) for i in range(0,len(piece))])
		return op


class BlokusPiece_I5(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "I5", [[1,1,1,1,1]])

class BlokusPiece_N(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "N", [[0,1,1,1],[1,1,0,0]])

class BlokusPiece_V5(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "V5", [[1,0,0],[1,0,0],[1,1,1]])

class BlokusPiece_T5(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "T5", [[0,1,0],[0,1,0],[1,1,1]])

class BlokusPiece_U(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "U", [[1,1,1],[1,0,1]])

class BlokusPiece_L5(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "L5", [[1,1,1,1],[1,0,0,0]])

class BlokusPiece_Y(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "Y", [[1,1,1,1],[0,1,0,0]])

class BlokusPiece_Z5(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "Z5", [[1,0,0],[1,1,1],[0,0,1]])

class BlokusPiece_W(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "W", [[1,0,0],[1,1,0],[0,1,1]])

class BlokusPiece_P(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "P", [[1,1],[1,1],[1,0]])

class BlokusPiece_X(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "X", [[0,1,0],[1,1,1],[0,1,0]])

class BlokusPiece_F(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "F", [[0,1,0],[1,1,1],[1,0,0]])

class BlokusPiece_Z4(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "Z4", [[1,0],[1,1],[0,1]])

class BlokusPiece_I4(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "I4", [[1,1,1,1]])

class BlokusPiece_L4(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "L4", [[1,1,1],[1,0,0]])

class BlokusPiece_O(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "O", [[1,1],[1,1]])

class BlokusPiece_T4(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "T4", [[0,1,0],[1,1,1]])

class BlokusPiece_I3(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "I3", [[1,1,1]])

class BlokusPiece_V3(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "V3", [[1,1],[0,1]])

class BlokusPiece_2(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "2", [[1,1]])

class BlokusPiece_1(BlokusPiece):
	def __init__(self):
		BlokusPiece.__init__(self, "1", [[1]])



