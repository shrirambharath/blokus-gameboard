"""Legal-move enumeration and frame translation.

The engine plays every seat from a board that has been rotated so the player
"starts at (0,0)". Humans, however, always see one global orientation. These
helpers enumerate legal placements in the rotated (engine) frame and translate
the resulting cell footprints back into global coordinates for display. The
opaque ``move_id`` round-trips the rotated-frame placement, so the client never
does any rule or rotation logic.
"""

import numpy as np
import gameboard
from gameboard import COLOR, ROTATION, UNPLAYED, PLAYED


def _coord_map(gridsize, rotation_index):
	"""Gr[r][c] = global flat index of the cell that sits at rotated-frame (r,c).

	The board is turned via np.rot90(global_grid, rotation_index); rotating a
	grid of global flat indices the same way gives an exact inverse lookup.
	"""
	flat = np.arange(gridsize * gridsize).reshape(gridsize, gridsize)
	return np.rot90(flat, rotation_index)


def rotated_to_global(coord_map, r, c, gridsize):
	idx = int(coord_map[r][c])
	return [idx // gridsize, idx % gridsize]


def display_orientation(orientation_grid, rotation_index):
	"""A piece-orientation grid as it appears in the global board frame."""
	return np.rot90(np.array(orientation_grid, int), -rotation_index).tolist()


def piece_orientations_global(piece, rotation_index):
	"""{engine_orientation_index: global_display_grid} for a piece."""
	return {idx: display_orientation(grid, rotation_index)
			for idx, grid in piece.piece_grid_orientations.items()}


def enumerate_placements(board, color, piece_name, orientation_filter=None):
	"""Enumerate every legal placement of ``piece_name`` for ``color``.

	The board MUST already be turned for ``color`` (rotated frame). Returns
	``{ orientation_index: [ {move_id, cells, anchor} ] }`` where ``cells`` and
	``anchor`` are in GLOBAL coordinates and ``move_id`` encodes the
	rotated-frame placement as ``"<piece>:<orientation>:<i>:<j>"``.
	"""
	unplayed = board.pieces[color][UNPLAYED]
	if piece_name not in unplayed:
		return {}

	piece = unplayed[piece_name]
	color_id = board.players[color][COLOR]
	rotation_index = board.players[color][ROTATION]
	gridsize = board.gridsize
	coord_map = _coord_map(gridsize, rotation_index)

	# candidate anchor corners in the rotated frame
	if len(board.pieces[color][PLAYED]) == 0:
		candidates = [(0, 0)]
	else:
		all_corners = gameboard.BlokusPlayerHelper.identify_corners(
			board.grid, color_id, update_skip_tracking=False, skip_state=board.skip_state)
		candidates = list(all_corners.get(color_id, set()))

	result = {}
	for o_index, piece_grid in piece.piece_grid_orientations.items():
		if orientation_filter is not None and o_index != orientation_filter:
			continue
		filled = [(di, dj)
				  for di in range(len(piece_grid))
				  for dj in range(len(piece_grid[0]))
				  if piece_grid[di][dj] == 1]
		placements = []
		seen = set()
		for (cr, cc) in candidates:
			# A legal placement only needs ONE of the piece's cells to touch the
			# corner candidate -- not necessarily its (0,0) cell. So try anchoring
			# each filled cell onto (cr,cc) and let the engine validate the rest.
			for (dr, dc) in filled:
				oi, oj = cr - dr, cc - dc
				if oi < 0 or oj < 0 or (oi, oj) in seen:
					continue
				if not board.validate_play_piece_helper(color, piece_grid, oi, oj):
					continue
				seen.add((oi, oj))
				cells = [rotated_to_global(coord_map, oi + di, oj + dj, gridsize)
						 for (di, dj) in filled]
				anchor = min(cells, key=lambda rc: (rc[0], rc[1]))
				move_id = "%s:%d:%d:%d" % (piece_name, o_index, oi, oj)
				placements.append({"move_id": move_id, "cells": cells, "anchor": anchor})
		if placements:
			result[o_index] = placements
	return result


def has_any_move(board, color):
	"""True if ``color`` has at least one legal placement (board already turned)."""
	for piece_name in list(board.pieces[color][UNPLAYED].keys()):
		if enumerate_placements(board, color, piece_name):
			return True
	return False
