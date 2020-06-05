import pytest
from .context import gameboard


def string_to_grid_results(s):
	line_no = 0
	results = {}
	grid = []

	options = { 'X': 1,'Y': 2,'Z': 3 }
	for line in s.split('\n'):
		line = line.strip()
		if len(line) == 0:
			continue

		gridline = []
		col_no = 0
		for c in list(line.strip()):
			if c in options:
				gridline += [0]
				step = options[c]
				s = results.get(step, set())
				s.add((line_no,col_no))
				results[step] = s

			else:
				gridline += [int(c)]

			col_no += 1
		line_no += 1

		grid += [gridline]
	
	return grid, results



def test_identify_i_j_candidates():
	s_gamegrid = """
					110000000000
					010000000000
					010000000000
					010X00000000
					X01000000000
					011000000000
					010X00000000
					X0X000000000
					000000000000
					000000000000
					000000000000
					000000000000
				"""
	grid, exp_results = string_to_grid_results(s_gamegrid)

	color_id = 1
	step = 1 #get the X's
	candidates = gameboard.BlokusPlayerHelper.identify_corners(grid, color_id)
	assert sorted(exp_results[step]) == sorted(candidates[color_id]), "Unexpected results"




def test_identify_i_j_candidates_2():
	s_gamegrid = """
					110000000000
					010000000000
					012220000000
					012X00000000
					X01000000000
					011220000000
					010X22000000
					X2X200000000
					220222000000
					200000000000
					000000000000
					000000000000
				"""
	grid, exp_results = string_to_grid_results(s_gamegrid)

	color_id = 1
	step = 1 #get the X's
	candidates = gameboard.BlokusPlayerHelper.identify_corners(grid, color_id)
	assert sorted(exp_results[step]) == sorted(candidates[color_id]), "Unexpected results"



