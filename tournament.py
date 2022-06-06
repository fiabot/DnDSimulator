from DnDToolkit import * 
from BasicAgents import * 
from MonsterManual import * 
from JinJerryAgent import * 
import random 
import time 



def make_unqiue(creatures):
    """
    make all creatures have 
    unique names 
    """

    names = {}

    for creature in creatures: 
        name = creature.name 
        if name in names:   
            creature.name = name + str(names[name]) 
            names[name] += 1 
        else:
            names[name] = 1

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
        players, monsters = create_identical_parties(player_class, monster_class, manual, size)
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
if __name__ == "__main__":
    results = tourament(JinJerryCreature, RandomCreature, 10, MANUAL, debug=True)
    print(results) 
    pass
