import pytest
from .context import gameboard



def string_to_grid(s):
	return [[int(item) for item in list(x.strip())] for x in s.split('\n') if len(x.strip()) > 0]


def test_board_setup():
	board = gameboard.BlokusBoard()
	assert board.gridsize == 20, "Size set incorrectly"
	assert len(board.players) == 4, "Players set incorrectly"
	assert board.current_player == None, "Current player set incorrectly"

	for i in range(0, board.gridsize):
		for j in range(0, board.gridsize):
			assert board.grid[i][j] == 0, "Initialization is incorrect"


def test_turn_board():
	board = gameboard.BlokusBoard(8)
	assert board.gridsize == 8, "Size set incorrectly"
	
	s_grid = """
		00001111
		00002222
		00003333
		00004444
		00000000
		00000000
		00000000
		00000000
	"""
	board.grid = string_to_grid(s_grid)

	for i in range(0, board.gridsize):
		for j in range(0, board.gridsize):
			expected = 0
			if i == 0 and j > 3:
				expected = 1
			if i == 1 and j > 3:
				expected = 2
			if i == 2 and j > 3:
				expected = 3
			if i == 3 and j > 3:
				expected = 4
			assert board.grid[i][j] == expected, "Initialization is incorrect"


	board.turn_board(gameboard.RED)
	assert board.current_player == gameboard.RED, "Current player set incorrectly"

	#verify board has been rotated and the 'L' has moved to top left corner
	for i in range(0, board.gridsize):
		for j in range(0, board.gridsize):
			expected = 0
			if i <= 3 and j == 0:
				expected = 1
			if i <= 3 and j == 1:
				expected = 2
			if i <= 3 and j == 2:
				expected = 3
			if i <= 3 and j == 3:
				expected = 4
			assert board.grid[i][j] == expected, "Grid has NOT been rotated"


	try:
		board.turn_board(gameboard.RED)
		assert False, "Show not come here"
	except gameboard.BoardStateException as e:
		assert True


def test_return_board():
	board = gameboard.BlokusBoard(8)
	assert board.gridsize == 8, "Size set incorrectly"
	

	board.turn_board(gameboard.RED)
	assert board.current_player == gameboard.RED, "Current player set incorrectly"
	
	s_grid = """
		12340000
		12340000
		12340000
		12340000
		00000000
		00000000
		00000000
		00000000
	"""
	#set top left hand corner 'L'
	board.grid = string_to_grid(s_grid)

	for i in range(0, board.gridsize):
		for j in range(0, board.gridsize):
			expected = 0
			if i <= 3 and j == 0:
				expected = 1
			if i <= 3 and j == 1:
				expected = 2
			if i <= 3 and j == 2:
				expected = 3
			if i <= 3 and j == 3:
				expected = 4
			assert board.grid[i][j] == expected, "Initialization is incorrect"


	try:
		board.return_board(gameboard.BLUE)
		assert False, "Show not come here"
	except gameboard.BoardStateException as e:
		assert True


	board.return_board(gameboard.RED)
	assert board.current_player == None, "Current player not reset to None"

	#verify board has been rotated and the 'L' has moved to top right corner
	for i in range(0, board.gridsize):
		for j in range(0, board.gridsize):
			expected = 0
			if i == 0 and j > 3:
				expected = 1
			if i == 1 and j > 3:
				expected = 2
			if i == 2 and j > 3:
				expected = 3
			if i == 3 and j > 3:
				expected = 4
			assert board.grid[i][j] == expected, "Grid has NOT been rotated"


def test_play_piece():
	board = gameboard.BlokusBoard()
	assert board.gridsize == 20, "Size set incorrectly"

	player = 'unknown'
	piece_name = 'I5'
	piece_orientation_index = -1
	coord_i = 0
	coord_j = 0

	try:
		board.play_piece(player, piece_name, piece_orientation_index, coord_i, coord_j)
		assert False, "Invalid user: should not come here"
	except gameboard.BoardStateException as e:
		assert True

	player = gameboard.RED
	try:
		board.play_piece(player, piece_name, piece_orientation_index, coord_i, coord_j)
		assert False, "Invalid current player: should not come here"
	except gameboard.BoardStateException as e:
		assert True

	board.turn_board(player)
	board.pieces[player][gameboard.PLAYED][piece_name] = board.pieces[player][gameboard.UNPLAYED].pop(piece_name)
	try:
		board.play_piece(player, piece_name, piece_orientation_index, coord_i, coord_j)
		assert False, "Invalid piece: should not come here"
	except gameboard.BoardStateException as e:
		assert True

	piece_name = 'unknown'
	try:
		board.play_piece(player, piece_name, piece_orientation_index, coord_i, coord_j)
		assert False, "Invalid unknown piece: should not come here"
	except gameboard.BoardStateException as e:
		assert True

	piece_name = 'I3'
	try:
		board.play_piece(player, piece_name, piece_orientation_index, coord_i, coord_j)
		assert False, "Invalid piece orientation: should not come here"
	except gameboard.BoardStateException as e:
		assert True

	piece_orientation_index = 0
	coord_i = 1
	coord_j = 1
	assert board.play_piece(player, piece_name, piece_orientation_index, coord_i, coord_j) == False, "Invalid coords"

	coord_i = 0
	coord_j = 0
	board.pieces[player][gameboard.PLAYED] = {}
	assert len(board.pieces[player][gameboard.PLAYED]) == 0, "Piece not yet moved to played"
	assert board.play_piece(player, piece_name, piece_orientation_index, coord_i, coord_j), "Valid move"
	assert len(board.pieces[player][gameboard.PLAYED]) == 1, "Piece moved to played"


def test_validate_play_piece_case0():
	board = gameboard.BlokusBoard(8)
	assert board.gridsize == 8, "Size set incorrectly"

	player = gameboard.BLUE
	s_grid = """
				010
				010
				111
			"""
	piece_grid = string_to_grid(s_grid)
	coord_i = 1
	coord_j = 1
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Invalid coords"
	assert error_reason == gameboard.INVALID_FIRST_MOVE, "Invalid coords"

	coord_i = 0
	coord_j = 0
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Piece grid does not fill (0,0)"
	assert error_reason == gameboard.INVALID_FIRST_MOVE, "Piece grid does not fill (0,0)"

	s_grid = """
				111
				010
				010
			"""
	piece_grid = string_to_grid(s_grid)
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == True, "Valid case 0 piece"
	assert error_reason == gameboard.NOT_APPLICABLE, "Valid case 0 piece"


def test_validate_play_piece_case1():
	board = gameboard.BlokusBoard(8)
	assert board.gridsize == 8, "Size set incorrectly"

	player = gameboard.BLUE
	piece_name = 'I5'
	board.pieces[player][gameboard.PLAYED][piece_name] = board.pieces[player][gameboard.UNPLAYED].pop(piece_name) # Skip past case 0

	s_gamegrid = """
					11001100
					01011100
					01000010
					00111110
					00000000
					00000000
					00000000
					00000000
				"""
	board.grid = string_to_grid(s_gamegrid)

	coord_i = 0
	coord_j = 2

	s_grid = """
				11
				10
				10
				10
			"""
	piece_grid = string_to_grid(s_grid)
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Doesn't fit test failed"
	assert error_reason == gameboard.BLOCK_OCCUPIED, "Doesn't fit test failed"

	coord_i = 4
	coord_j = 7
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Out of bounds test failed"
	assert error_reason == gameboard.OUT_OF_GRID, "Out of bounds test failed"


def test_validate_play_piece_case2_type1():
	board = gameboard.BlokusBoard(8)
	assert board.gridsize == 8, "Size set incorrectly"

	player = gameboard.BLUE
	piece_name = 'I5'
	board.pieces[player][gameboard.PLAYED][piece_name] = board.pieces[player][gameboard.UNPLAYED].pop(piece_name) # Skip past case 0

	# Scenarios from here - https://docs.google.com/spreadsheets/d/1oyHOQIKF13vacMIbzlxpl9qaU5U82RcDIpwUpxNLlNA/edit?usp=sharing
	s_gamegrid = """
					11000000
					01000000
					01000000
					01011110
					00100000
					01100000
					01000000
					00000000
				"""
	board.grid = string_to_grid(s_gamegrid)

	s_grid = """
				110
				011
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 0
	coord_j = 2
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 1
	coord_j = 5
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 4
	coord_j = 5
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 6
	coord_j = 2
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"


	#changing the orientation of the piece in the same grid
	s_grid = """
				10
				11
				01
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 0
	coord_j = 2
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 0
	coord_j = 5
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 4
	coord_j = 6
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 5
	coord_j = 3
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"


def test_validate_play_piece_case2_type2():
	board = gameboard.BlokusBoard(8)
	assert board.gridsize == 8, "Size set incorrectly"

	player = gameboard.BLUE
	piece_name = 'I5'
	board.pieces[player][gameboard.PLAYED][piece_name] = board.pieces[player][gameboard.UNPLAYED].pop(piece_name) # Skip past case 0

	# Scenarios from here - https://docs.google.com/spreadsheets/d/1oyHOQIKF13vacMIbzlxpl9qaU5U82RcDIpwUpxNLlNA/edit?usp=sharing
	s_gamegrid = """
					11100000
					00100000
					00100000
					00101111
					00010000
					00110000
					00100000
					00000000
				"""
	board.grid = string_to_grid(s_gamegrid)

	s_grid = """
				110
				011
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 0
	coord_j = 3
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 3
	coord_j = 0
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 6
	coord_j = 0
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 4
	coord_j = 5
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 5
	coord_j = 4
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"


	#changing the orientation of the piece in the same grid
	s_grid = """
				10
				11
				01
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 1
	coord_j = 0
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"

	coord_i = 5
	coord_j = 0
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"


	#changing the piece in the same grid
	s_grid = """
				10
				10
				10
				11
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 1
	coord_j = 0
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"


	#changing the piece in the same grid
	s_grid = """
				0001
				1111
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 6
	coord_j = 1
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "Contiguous Blocks"
	assert error_reason == gameboard.CONTIGUOUS_BLOCKS, "Contiguous Blocks"




def test_validate_play_piece_case3():
	board = gameboard.BlokusBoard(8)
	assert board.gridsize == 8, "Size set incorrectly"

	player = gameboard.BLUE
	piece_name = 'I5'
	board.pieces[player][gameboard.PLAYED][piece_name] = board.pieces[player][gameboard.UNPLAYED].pop(piece_name) # Skip past case 0

	# Scenarios from here - https://docs.google.com/spreadsheets/d/1oyHOQIKF13vacMIbzlxpl9qaU5U82RcDIpwUpxNLlNA/edit?usp=sharing
	s_gamegrid = """
					11000022
					01000022
					01022200
					01000000
					00100000
					01100000
					01000000
					00000022
				"""
	board.grid = string_to_grid(s_gamegrid)

	s_grid = """
				011
				110
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 0
	coord_j = 3
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "No corner"
	assert error_reason == gameboard.NO_CORNER, "No corner"

	coord_i = 3
	coord_j = 5
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "No corner"
	assert error_reason == gameboard.NO_CORNER, "No corner"

	coord_i = 6
	coord_j = 4
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "No corner"
	assert error_reason == gameboard.NO_CORNER, "No corner"

	
	s_grid = """
				01
				11
				10
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 2
	coord_j = 6
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "No corner"
	assert error_reason == gameboard.NO_CORNER, "No corner"

	coord_i = 5
	coord_j = 4
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "No corner"
	assert error_reason == gameboard.NO_CORNER, "No corner"

	coord_i = 5
	coord_j = 5
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "No corner"
	assert error_reason == gameboard.NO_CORNER, "No corner"

	
	s_grid = """
				10
				11
				01
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 3
	coord_j = 6
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == False, "No corner"
	assert error_reason == gameboard.NO_CORNER, "No corner"




def test_validate_play_piece_valid():
	board = gameboard.BlokusBoard(8)
	assert board.gridsize == 8, "Size set incorrectly"

	player = gameboard.BLUE
	piece_name = 'I5'
	board.pieces[player][gameboard.PLAYED][piece_name] = board.pieces[player][gameboard.UNPLAYED].pop(piece_name) # Skip past case 0

	# Scenarios from here - https://docs.google.com/spreadsheets/d/1oyHOQIKF13vacMIbzlxpl9qaU5U82RcDIpwUpxNLlNA/edit?usp=sharing
	s_gamegrid = """
					11000022
					01000022
					01022200
					01000000
					00100000
					01100000
					01000000
					00000022
				"""
	board.grid = string_to_grid(s_gamegrid)

	s_grid = """
				01
				11
				10
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 5
	coord_j = 3
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == True, "Valid"
	assert error_reason == gameboard.NOT_APPLICABLE, "Valid"


	s_grid = """
				110
				011
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 3
	coord_j = 3
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == True, "Valid"
	assert error_reason == gameboard.NOT_APPLICABLE, "Valid"

	coord_i = 6
	coord_j = 3
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == True, "Valid"
	assert error_reason == gameboard.NOT_APPLICABLE, "Valid"


	s_grid = """
				1
			"""
	piece_grid = string_to_grid(s_grid)

	# testing same piece/orientation in various locations
	coord_i = 3
	coord_j = 3
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == True, "Valid"
	assert error_reason == gameboard.NOT_APPLICABLE, "Valid"

	coord_i = 4
	coord_j = 0
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == True, "Valid"
	assert error_reason == gameboard.NOT_APPLICABLE, "Valid"

	coord_i = 6
	coord_j = 3
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == True, "Valid"
	assert error_reason == gameboard.NOT_APPLICABLE, "Valid"

	coord_i = 7
	coord_j = 0
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == True, "Valid"
	assert error_reason == gameboard.NOT_APPLICABLE, "Valid"

	coord_i = 7
	coord_j = 2
	is_valid_move, error_reason = board._validate_play_piece(player, piece_grid, coord_i, coord_j) 
	assert is_valid_move == True, "Valid"
	assert error_reason == gameboard.NOT_APPLICABLE, "Valid"

