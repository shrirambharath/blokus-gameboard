import pytest
from .context import gameboard


def test_block_counts():
	_I5 = gameboard.BlokusPiece_I5()
	_N = gameboard.BlokusPiece_N()
	_V5 = gameboard.BlokusPiece_V5()
	_T5 = gameboard.BlokusPiece_T5()
	_U = gameboard.BlokusPiece_U()
	_L5 = gameboard.BlokusPiece_L5()
	_Y = gameboard.BlokusPiece_Y()
	_Z5 = gameboard.BlokusPiece_Z5()
	_W = gameboard.BlokusPiece_W()
	_P = gameboard.BlokusPiece_P()
	_X = gameboard.BlokusPiece_X()
	_F = gameboard.BlokusPiece_F()
	_Z4 = gameboard.BlokusPiece_Z4()
	_I4 = gameboard.BlokusPiece_I4()
	_L4 = gameboard.BlokusPiece_L4()
	_O = gameboard.BlokusPiece_O()
	_T4 = gameboard.BlokusPiece_T4()
	_I3 = gameboard.BlokusPiece_I3()
	_V3 = gameboard.BlokusPiece_V3()
	_2 = gameboard.BlokusPiece_2()
	_1 = gameboard.BlokusPiece_1()

	assert _I5.block_count == 5, "I5 block count failed"
	assert _N.block_count == 5, "N block count failed"
	assert _V5.block_count == 5, "V5 block count failed"
	assert _T5.block_count == 5, "T5 block count failed"
	assert _U.block_count == 5, "U block count failed"
	assert _L5.block_count == 5, "L5 block count failed"
	assert _Y.block_count == 5, "Y block count failed"
	assert _Z5.block_count == 5, "Z5 block count failed"
	assert _W.block_count == 5, "W block count failed"
	assert _P.block_count == 5, "P block count failed"
	assert _X.block_count == 5, "X block count failed"
	assert _F.block_count == 5, "F block count failed"
	assert _Z4.block_count == 4, "Z4 block count failed"
	assert _I4.block_count == 4, "I4 block count failed"
	assert _L4.block_count == 4, "L4 block count failed"
	assert _O.block_count == 4, "O block count failed"
	assert _T4.block_count == 4, "T4 block count failed"
	assert _I3.block_count == 3, "I3 block count failed"
	assert _V3.block_count == 3, "V3 block count failed"
	assert _2.block_count == 2, "2 block count failed"
	assert _1.block_count == 1, "1 block count failed"


def test_piece_grid_orientations():
	_I5 = gameboard.BlokusPiece_I5()
	_N = gameboard.BlokusPiece_N()
	_V5 = gameboard.BlokusPiece_V5()
	_T5 = gameboard.BlokusPiece_T5()
	_U = gameboard.BlokusPiece_U()
	_L5 = gameboard.BlokusPiece_L5()
	_Y = gameboard.BlokusPiece_Y()
	_Z5 = gameboard.BlokusPiece_Z5()
	_W = gameboard.BlokusPiece_W()
	_P = gameboard.BlokusPiece_P()
	_X = gameboard.BlokusPiece_X()
	_F = gameboard.BlokusPiece_F()
	_Z4 = gameboard.BlokusPiece_Z4()
	_I4 = gameboard.BlokusPiece_I4()
	_L4 = gameboard.BlokusPiece_L4()
	_O = gameboard.BlokusPiece_O()
	_T4 = gameboard.BlokusPiece_T4()
	_I3 = gameboard.BlokusPiece_I3()
	_V3 = gameboard.BlokusPiece_V3()
	_2 = gameboard.BlokusPiece_2()
	_1 = gameboard.BlokusPiece_1()

	assert len(_I5.piece_grid_orientations) == 2, "I5 number orientations failed"
	assert len(_N.piece_grid_orientations) == 8, "N number orientations failed"
	assert len(_V5.piece_grid_orientations) == 4, "V5 number orientations failed"
	assert len(_T5.piece_grid_orientations) == 4, "T5 number orientations failed"
	assert len(_U.piece_grid_orientations) == 4, "U number orientations failed"
	assert len(_L5.piece_grid_orientations) == 8, "L5 number orientations failed"
	assert len(_Y.piece_grid_orientations) == 8, "Y number orientations failed"
	assert len(_Z5.piece_grid_orientations) == 4, "Z5 number orientations failed"
	assert len(_W.piece_grid_orientations) == 4, "W number orientations failed"
	assert len(_P.piece_grid_orientations) == 8, "P number orientations failed"
	assert len(_X.piece_grid_orientations) == 1, "X number orientations failed"
	assert len(_F.piece_grid_orientations) == 8, "F number orientations failed"
	assert len(_Z4.piece_grid_orientations) == 4, "Z4 number orientations failed"
	assert len(_I4.piece_grid_orientations) == 2, "I4 number orientations failed"
	assert len(_L4.piece_grid_orientations) == 8, "L4 number orientations failed"
	assert len(_O.piece_grid_orientations) == 1, "O number orientations failed"
	assert len(_T4.piece_grid_orientations) == 4, "T4 number orientations failed"
	assert len(_I3.piece_grid_orientations) == 2, "I3 number orientations failed"
	assert len(_V3.piece_grid_orientations) == 4, "V3 number orientations failed"
	assert len(_2.piece_grid_orientations) == 2, "2 number orientations failed"
	assert len(_1.piece_grid_orientations) == 1, "1 number orientations failed"
