
import gameboard

def main():
	player1 = gameboard.BlokusRandomPlayer()
	player2 = gameboard.BlokusRandomPlayer()
	player3 = gameboard.BlokusRandomPlayer()
	player4 = gameboard.BlokusRandomPlayer()

	b = gameboard.BlokusGame(player1, player2, player3, player4, visualize=False, visualizeTimer=5, gridsize=20)
	b.setup_game()
	b.play_game()


main()