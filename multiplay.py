#!/usr/bin/env python

import gameboard
import time, argparse


def get_player(p_type):
	if p_type == gameboard.RANDOM_PLAYER:
		return gameboard.BlokusRandomPlayer()

	raise gameboard.BoardStateException("Unknown player type: %s" % p_type)



def play_single_game(player_types):
	if len(player_types) != 4:
		raise gameboard.BoardStateException("Invalid player types initialization")

	player1 = get_player(player_types[0])
	player2 = get_player(player_types[1])
	player3 = get_player(player_types[2])
	player4 = get_player(player_types[3])

	game = gameboard.BlokusGame(player1, player2, player3, player4, visualize=False, visualizeTimer=5, gridsize=20)
	game.setup_game()
	game.play_game()

	return game



def update_game_stats(game, player_record):
	game_final_scores = game.final_scores
	game_start_sequence = game.start_sequence

	player_win_record = player_record['win']
	player_score_record = player_record['score']
	player_turn_record = player_record['turn']
	player_name_record = player_record['names']
	
	# {'blue': 58, 'red': 36, 'yellow': 51, 'green': 60}
	leading_score = 0
	leader = None

	for (player, player_score) in game_final_scores.items():
		(best_score, running_total_score, num_scores) = player_score_record[player]
		if best_score < player_score:
			best_score = player_score
		running_total_score += player_score
		num_scores += 1
		player_score_record[player] = (best_score, running_total_score, num_scores)

		if player_score > leading_score:
			leading_score = player_score
			leader = player

	win_record = player_win_record[leader]
	player_win_record[leader] = win_record + 1

	for index in range(0,len(game_start_sequence)):
		player = game_start_sequence[index]
		(num_starts, running_total_start_positions, num_entries) = player_turn_record[player]
		if index == 0:
			num_starts += 1
		running_total_start_positions += index
		num_entries += 1

		player_turn_record[player] = (num_starts, running_total_start_positions, num_entries)

	for (player, player_obj) in game.players.items():
		player_name_record[player] = player_obj.player_name

	player_record['win'] = player_win_record
	player_record['score'] = player_score_record
	player_record['turn'] = player_turn_record
	player_record['names'] = player_name_record

	return player_record


def print_results(system_stats, player_record):
	player_win_record = player_record['win']
	player_score_record = player_record['score']
	player_turn_record = player_record['turn']
	player_name_record = player_record['names']

	print("Games played: %d" % len(system_stats))
	print("Shortest game: %d msecs" % min(system_stats))
	print("Longest game: %d msecs" % max(system_stats))
	print("Average game length: %d msecs" % (sum(system_stats) / len(system_stats)))

	for player in player_win_record.keys():
		player_name = player_name_record[player]
		win_pct = float(player_win_record[player]) * 100.0 / float(len(system_stats))

		(best_score, running_total_score, num_scores) = player_score_record[player]
		avg_score = float(running_total_score) / float(num_scores)

		(num_starts, running_total_start_positions, num_entries) = player_turn_record[player]
		avg_start = float(running_total_start_positions) / float(num_entries)

		print("\tPlayer: %s, Win %%: %.2f, Starts: %d, AvgStart: %.2f, Best game score: %d, Avg game score: %.2f" % (player_name, win_pct, num_starts, avg_start, best_score, avg_score))
	print("\n")


def run(player_types, num_games=10, screen_update=10):
	player_record = {
		'win': { gameboard.BLUE: 0, gameboard.YELLOW: 0, gameboard.GREEN: 0, gameboard.RED: 0 },
		'score': { gameboard.BLUE: (0,0,0), gameboard.YELLOW: (0,0,0), gameboard.GREEN: (0,0,0), gameboard.RED: (0,0,0) }, #(best score, running total, num scores)
		'turn': { gameboard.BLUE: (0,0,0), gameboard.YELLOW: (0,0,0), gameboard.GREEN: (0,0,0), gameboard.RED: (0,0,0) }, #(num starts, running total start positions, num entries)
		'names': { gameboard.BLUE: None, gameboard.YELLOW: None, gameboard.GREEN: None, gameboard.RED: None }
	}

	system_stats = []

	for game_id in range(0,num_games):
		start = int(round(time.time() * 1000))
		game = play_single_game(player_types)
		stop = int(round(time.time() * 1000))

		system_stats += [(stop-start)]
		player_record = update_game_stats(game, player_record)

		if screen_update > 0 and len(system_stats) > 0 and len(system_stats) % screen_update == 0:
			print_results(system_stats, player_record)

	print("\n\nFinal:")
	print_results(system_stats, player_record)




def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', type=int, dest='game_count', required=True, help="Number of games to run")
	parser.add_argument('-s', type=int, default=0, dest='screen_update_count', required=False, help="Intermediate result update")
	parser.add_argument('-p1', default=gameboard.RANDOM_PLAYER, dest='p1', required=False, help="Player 1 type")
	parser.add_argument('-p2', default=gameboard.RANDOM_PLAYER, dest='p2', required=False, help="Player 2 type")
	parser.add_argument('-p3', default=gameboard.RANDOM_PLAYER, dest='p3', required=False, help="Player 3 type")
	parser.add_argument('-p4', default=gameboard.RANDOM_PLAYER, dest='p4', required=False, help="Player 4 type")
	args = parser.parse_args()

	players = [args.p1, args.p2, args.p3, args.p4]
	run(players, args.game_count, args.screen_update_count)


main()

