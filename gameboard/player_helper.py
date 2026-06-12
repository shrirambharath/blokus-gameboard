import gameboard 

class BlokusPlayerHelper:
	# ALL static members
	ZONE_DEPTH = 3
	skip_next_time_set = {}

	# Helpers to speed up going through the entire grid based on previous runs.
	# skip_state lets a caller (e.g. a web GameSession) keep its own per-game skip
	# cache so concurrent games don't corrupt each other. When skip_state is None we
	# fall back to the process-global cache, preserving the original sim behavior.
	def reset_skips():
		BlokusPlayerHelper.skip_next_time_set = {}
	def _skip_store(skip_state):
		return BlokusPlayerHelper.skip_next_time_set if skip_state is None else skip_state
	def skip(i, j, color_id, skip_state=None):
		store = BlokusPlayerHelper._skip_store(skip_state)
		return (i,j) in store.get(color_id,set())
	def skip_next_time(i, j, color_id, skip_state=None):
		store = BlokusPlayerHelper._skip_store(skip_state)
		s = store.get(color_id, set())
		s.add((i,j))
		store[color_id] = s

	def adjacent(i, j, grid, color_id, gridsize):
		if (i>0 and grid[i-1][j] == color_id) or \
			(i<gridsize-1 and grid[i+1][j] == color_id) or \
			(j>0 and grid[i][j-1] == color_id) or \
			(j<gridsize-1 and grid[i][j+1] == color_id):
			return True
		else:
			return False

	def identify_corners(grid, turn_color_id, update_skip_tracking=True, skip_state=None):
		gridsize = len(grid)
		_candidates = { }

		for i in range(0,gridsize):
			for j in range(0,gridsize):
				if grid[i][j] == 0: #nothing on this spot
					continue

				color_id = grid[i][j]
				if color_id not in _candidates:
					_candidates[color_id] = set()

				if BlokusPlayerHelper.skip(i, j, turn_color_id, skip_state):
					# previous run identified this block as skippable
					continue

				#test the diagonally adjacent blocks for adjacents
				added_at_least_one = False
				if i>0 and j>0 and grid[i-1][j-1] == 0 and not BlokusPlayerHelper.adjacent(i-1, j-1, grid, color_id, gridsize):
					_candidates[color_id].add((i-1,j-1))
					added_at_least_one = True
				if i>0 and j<gridsize-1 and grid[i-1][j+1] == 0 and not BlokusPlayerHelper.adjacent(i-1, j+1, grid, color_id, gridsize):
					_candidates[color_id].add((i-1,j+1))
					added_at_least_one = True
				if i<gridsize-1 and j>0 and grid[i+1][j-1] == 0 and not BlokusPlayerHelper.adjacent(i+1, j-1, grid, color_id, gridsize):
					_candidates[color_id].add((i+1,j-1))
					added_at_least_one = True
				if i<gridsize-1 and j<gridsize-1 and grid[i+1][j+1] == 0 and not BlokusPlayerHelper.adjacent(i+1, j+1, grid, color_id, gridsize):
					_candidates[color_id].add((i+1,j+1))
					added_at_least_one = True

				if update_skip_tracking:
					if not added_at_least_one:
						BlokusPlayerHelper.skip_next_time(i, j, turn_color_id, skip_state)

		return _candidates

