#!/usr/bin/env python

import gameboard
import time, argparse
from prettytable import PrettyTable

def get_player(p_type):
	if p_type == gameboard.RANDOM_PLAYER:
		return gameboard.BlokusRandomPlayer()
	elif p_type == gameboard.GREEDY_PLAYER:
		return gameboard.BlokusGreedyPlayer()
	elif p_type == gameboard.GREEDY_LOOKAHEAD_PLAYER:
		return gameboard.BlokusGreedyLookAheadPlayer()

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

	player_finish_record = player_record['finish']
	player_score_record = player_record['score']
	player_turn_record = player_record['turn']
	player_name_record = player_record['names']
	
	# {'blue': 58, 'red': 36, 'yellow': 51, 'green': 60}
	for (player, player_score) in game_final_scores.items():
		(best_score, running_total_score, num_scores) = player_score_record[player]
		if best_score < player_score:
			best_score = player_score
		running_total_score += player_score
		num_scores += 1
		player_score_record[player] = (best_score, running_total_score, num_scores)


	finish_order = sorted(game_final_scores.items(), key=lambda x:x[1], reverse=True) 
	for finish in range(0,len(finish_order)):
		player = finish_order[finish][0]
		(f1, f2, f3, f4) = player_finish_record[player]

		if finish == 0:
			f1 += 1; 
		elif finish == 1:
			f2 += 1;
		elif finish ==2:
			f3 += 1; 
		else:
			f4 += 1; 
		player_finish_record[player] = (f1, f2, f3, f4)


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

	player_record['finish'] = player_finish_record
	player_record['score'] = player_score_record
	player_record['turn'] = player_turn_record
	player_record['names'] = player_name_record
	if 'order' not in player_record:
		player_record['order'] = game.turn_order

	return player_record


def print_results(system_stats, player_record):
	player_finish_record = player_record['finish']
	player_score_record = player_record['score']
	player_turn_record = player_record['turn']
	player_name_record = player_record['names']
	player_turn_order = player_record['order']

	print("\n\n")
	print("Games played: %d" % len(system_stats))
	print("Shortest game: %d msecs" % min(system_stats))
	print("Longest game: %d msecs" % max(system_stats))
	print("Average game length: %d msecs" % (sum(system_stats) / len(system_stats)))

	t = PrettyTable(['Name', 'Finish 1st', 'Finish 2nd', 'Finish 3rd', 'Finish 4th', 'Avg Finish', 'Starts', 'Avg Start', 'Best Score', 'Avg Score'])

	for player in player_turn_order:
		player_name = player_name_record[player]
		_f1_pct = float(player_finish_record[player][0]) / float(len(system_stats))
		_f2_pct = float(player_finish_record[player][1]) / float(len(system_stats))
		_f3_pct = float(player_finish_record[player][2]) / float(len(system_stats))
		_f4_pct = float(player_finish_record[player][3]) / float(len(system_stats))
		_avg_finish = ((1.0 * float(player_finish_record[player][0])) + (2.0 * float(player_finish_record[player][1])) + \
			(3.0 * float(player_finish_record[player][2])) + (4.0 * float(player_finish_record[player][3]))) / \
			float(player_finish_record[player][0] + player_finish_record[player][1] + player_finish_record[player][2] + player_finish_record[player][3])

		(best_score, running_total_score, num_scores) = player_score_record[player]
		avg_score = float(running_total_score) / float(num_scores)

		(num_starts, running_total_start_positions, num_entries) = player_turn_record[player]
		avg_start = float(running_total_start_positions) / float(num_entries)

		t.add_row([player_name, '%.2f' % _f1_pct, '%.2f' % _f2_pct, '%.2f' % _f3_pct, '%.2f' % _f4_pct, '%.2f' % _avg_finish, 
			num_starts, '%.2f' % avg_start, best_score, '%.2f' % avg_score])

	print(t)
	print("\n\n")


def run(player_types, num_games=10, screen_update=10):
	player_record = {
		'finish': { gameboard.BLUE: (0,0,0,0), gameboard.YELLOW: (0,0,0,0), gameboard.GREEN: (0,0,0,0), gameboard.RED: (0,0,0,0) }, #( # 1st, # 2nd, # 3rd, # 4th)
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

