import gameboard 

class BlokusPlayerHelper:
	# ALL static members
	ZONE_DEPTH = 3
	skip_next_time_set = {}

	# Helpers to speed up going through the entire grid based on previous runs
	def reset_skips():
		BlokusPlayerHelper.skip_next_time_set = {}
	def skip(i, j, color_id):
		return (i,j) in BlokusPlayerHelper.skip_next_time_set.get(color_id,set())
	def skip_next_time(i, j, color_id):
		s = BlokusPlayerHelper.skip_next_time_set.get(color_id, set())
		s.add((i,j))
		BlokusPlayerHelper.skip_next_time_set[color_id] = s

	def adjacent(i, j, grid, color_id, gridsize):
		if (i>0 and grid[i-1][j] == color_id) or \
			(i<gridsize-1 and grid[i+1][j] == color_id) or \
			(j>0 and grid[i][j-1] == color_id) or \
			(j<gridsize-1 and grid[i][j+1] == color_id):
			return True
		else:
			return False

	def identify_corners(grid, turn_color_id, update_skip_tracking=True):
		gridsize = len(grid)
		_candidates = { }

		for i in range(0,gridsize):
			for j in range(0,gridsize):
				if grid[i][j] == 0: #nothing on this spot
					continue

				color_id = grid[i][j]
				if color_id not in _candidates:
					_candidates[color_id] = set()

				if BlokusPlayerHelper.skip(i, j, turn_color_id):
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
						BlokusPlayerHelper.skip_next_time(i, j, turn_color_id)

		return _candidates

