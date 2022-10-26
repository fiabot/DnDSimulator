import itertools
from DnDToolkit import * 
from BasicAgents import * 
from MonsterManual import * 
from JinJerryAgent import * 
import random 
import time 


def tourament(player_class, monster_class, game_count, manual, min_size = 2, max_size = 5, grid_size = 20, debug = False, round_limit = 20):
    map = Grid(grid_size, grid_size, space = 1)
    results = {PLAYERTEAM:0, MONSTERTEAM:0, TIE:0, INCOMPLETE:0}

    for game in range(game_count): 
        
        if debug:
            start = time.perf_counter() 

        # clear grid 
        map.clear_grid() 

        # creatue new parties 
        size = random.randrange(min_size, max_size)
        players, monsters = create_random_identical_parties(player_class, monster_class, manual, size)
        make_unqiue(monsters + players)

        if debug:
            print("\n\n\nGame {} of {}".format(game, game_count))
            print("Current results {}".format(results))
            print("Party Size {}".format(size))
            print("\nMonsters:")
            for monster in monsters:
                print(monster)
            
            print("\nPlayers:")
            for player in players:
                print(player)

        # create starting positions 
        monster_pos = [] 
        player_pos = [] 
        for i in range(size):
            monster_pos.append((0, i)) # monsters at top left 
            player_pos.append((grid_size - 1, grid_size - i - 1)) # players at bottom right 
        
        # create game 
        game = Game(players, monsters, player_pos, monster_pos, map)

        # play game 
        winner = game.play_game(round_limit= round_limit)
        results[winner[0]] += 1 

        if debug:
            end = time.perf_counter() 
            print(f"Time: {end - start:0.4f}")
    return results 

def multi_agent_touranment(agent_classes, trial_count, manual, min_size = 2, max_size = 5, grid_size = 10, debug = False, round_limit = 20):
    results = {} 
    map = Grid(grid_size, grid_size, space = 1) 


    combinations = itertools.combinations(agent_classes, 2)
    
    for combo in combinations:
        player_class = combo[0]
        monster_class = combo[1]

        player_wins = 0 
        monster_wins = 0 
        incomp = 0 

        player_times = [] 
        monster_times = [] 

        rounds= [] 

        for game_count in range(trial_count):

            if debug:
                start = time.perf_counter() 

            # clear grid 
            map.clear_grid() 

            # creatue new parties 
            size = random.randrange(min_size, max_size)
            players, monsters = create_random_identical_parties(player_class, monster_class, manual, size)
            make_unqiue(monsters + players)

            if debug:
                print("\n\n\nGame {} of {}".format(game_count, trial_count))
                print("Current results {}".format(results))
                print("Party Size {}".format(size))
                print("\nMonsters:")
                for monster in monsters:
                    print(monster)
                
                print("\nPlayers:")
                for player in players:
                    print(player)

            # create starting positions 
            monster_pos = [] 
            player_pos = [] 
            for i in range(size):
                monster_pos.append((0, i)) # monsters at top left 
                player_pos.append((grid_size - 1, grid_size - i - 1)) # players at bottom right 
            
            # create game 
            game = Game(players, monsters, player_pos, monster_pos, map)

            # play game 
            winner = game.play_game(round_limit= round_limit)

            
            for player in game.players:
                if hasattr(player, "times"):
                    t = player.average_time()
                    if t> 0:
                        player_times.append(t)
            
            for monster in game.monsters:
                if hasattr(monster, "times"):
                    t = monster.average_time()
                    if t > 0:
                        monster_times.append(t)   
            
            if winner[0] == PLAYERTEAM:
                player_wins += 1 
            elif winner[0] == MONSTERTEAM:
                monster_wins += 1 
            else:
                incomp += 1 

            if winner[1] > round_limit:
                print("ERROR WITH ROUND:{}".format(winner[1]))
            
            rounds.append(winner[1])

            if debug:
                end = time.perf_counter() 
                print(f"Time: {end - start:0.4f}")

        if len(rounds) > 0:
            round_av = sum(rounds) / len(rounds)
        else:
            round_av = -1
        if len(player_times) != 0:
            ptime = sum(player_times) / len(player_times)

        else: 
            ptime = -1 
        player_dict = {"vs": monster_class.__name__, "wins": player_wins, "losses": monster_wins, "ties": incomp, "times": ptime, "avg rounds": round_av}

        if player_class.__name__ in results:
            results[player_class.__name__].append(player_dict)
        else:
            results[player_class.__name__] = [player_dict]

        if len(monster_times) != 0:
            mtime = sum(monster_times) / len(monster_times)
        else: 
            mtime = -1 
        monster_dict = {"vs": player_class.__name__, "wins": monster_wins, "losses": player_wins, "ties": incomp, "times": mtime, "avg rounds": round_av}

        if monster_class.__name__ in results:
            results[monster_class.__name__].append(monster_dict)
        else:
            results[monster_class.__name__] = [monster_dict]
    return results


if __name__ == "__main__":
    results = tourament(JinJerryCreature, RandomCreature, 10, MANUAL, debug=True)
    print(results) 
    pass
