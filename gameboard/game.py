import gameboard 
import time, random

class BlokusGame:
	def __init__(self, player1, player2, player3, player4, visualize=False, visualizeTimer = 10, gridsize=20):
		self.board = gameboard.BlokusBoard(gridsize)
		self.players = {
			gameboard.BLUE: player1,
			gameboard.RED: player2,
			gameboard.YELLOW: player3,
			gameboard.GREEN: player4
		}
		self.visualize = visualize
		self.visualizeTimer = visualizeTimer
		self.final_scores = {}

		player1.assign_color(gameboard.BLUE)
		player2.assign_color(gameboard.RED)
		player3.assign_color(gameboard.YELLOW)
		player4.assign_color(gameboard.GREEN)


	def setup_game(self):
		#turn tracking 
		self.turn_order = [gameboard.BLUE, gameboard.RED, gameboard.YELLOW, gameboard.GREEN]
		self.current_turn_index = random.randint(0,3)

		#for game stats collection later
		self.start_sequence = [self.turn_order[(self.current_turn_index + i) % 4] for i in range(0,4)]
		

	def play_game(self):
		done_players = set()

		while len(done_players) < len(self.players):
			current_player = self.players[self.turn_order[self.current_turn_index]]
			self.current_turn_index = (self.current_turn_index + 1) % len(self.players)
			if current_player.color in done_players:
				#this player has no moves left
				continue
		
			self.board.turn_board(current_player.color)
			
			(piece, piece_orientation_index, coord_i, coord_j) = current_player.make_move(self.board)
			if piece is None:
				#current player is done with moves
				done_players.add(current_player.color)
			else:	
				self.board.play_piece(current_player.color, piece.piece_name, piece_orientation_index, coord_i, coord_j)

			self.board.return_board(current_player.color)

			
			if self.visualize:
				self.board.pretty_print()
				time.sleep(self.visualizeTimer)


		self.finalize_scores()


	def finalize_scores(self):
		for player in self.board.pieces.keys():
			played_pieces = self.board.pieces[player][gameboard.PLAYED]

			piece_points = [piece.block_count for piece in played_pieces]
			if len(piece_points) == 21:
				#bonus points
				if piece_points[-1] == 1:
					#monomino
					points = 20
				else:
					points = 15
			else:
				points = 0
			points += sum(piece_points)

			self.final_scores[player] = points


		if self.visualize:
			self.board.pretty_print()
			print (self.final_scores)
