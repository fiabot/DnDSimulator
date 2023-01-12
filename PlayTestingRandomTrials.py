from DnDToolkit import *
from JinJerryAgent import JinJerryCreature 
from MonsterManual import *
from RuleBasedAgents import AggressiveCreature, ProtectiveCreature
#from ShyneAgent import ShyneCreature 
import jsonpickle
from DMGToolkit import * 

"""
Randomly create 
play testing scenarios 
and records stats from play tests 

"""
"""
Easy 
Temp 1 
    Level 0.125 * 3 
Temp 2 
    Level 0,125 * 1
    Level 0.25 * 1 
Temp 3 
    Level 0.5 * 1 

Medium 
Temp1 
    Level 0.125 * 5 
Temp 2 
    Level 0.125 * 3
    Level 0.25 * 1 
Temp 2 
    Level 0.125 * 1
    Level 0.25 * 2

Temp 6 
    Level 0.25 * 1 
    Level 0.5 * 1 
Temp 5 
    Level 1 * 1 

Hard 
Temp 1 
    Level 0.5 * 1 
    Level 0.125 * 3 
Temp 2 
    Level 0.5 * 1 
    Level 0.25 * 1 
    Level 0.125 * 1 
Temp 4 
    0.25 * 4 
Temp 5 
    Level 0.25 * 3 
    Level 0.125 * 1 
Temp 3 
    Level 1 * 1 
    Level 0.25 * 1 
Temp 3 
    Level 0.125 * 3 
    Level 0.25 * 2

Deadly 
Temp 1 
    Level 1 * 1 
    Level 0.125 * 2 
Temp 2 
    Level 0.5 * 2 
    Level 0.125 * 2 
Temp 3 
    Level 0.5 * 2 
    Level 0.25 * 1 
Temp 5 
    Level 0.25 * 5 
Temp 6 
    Level 0.5 * 1 
    Level 0.25 * 3 

"""



def play_random_games(name, agent_class, players, trial_length, round_limit = 20):
    length = random.randint(1, 5)
    monsters = create_random_party(agent_class, MONSTER_MANUAL, length)
    monsters = [monster for monster in monsters if not monster is None]
    diff = predict_difficuly(monsters)
    grid = Grid(7, 7)

    player_pos, monster_pos = set_positions(len(players), len(monsters))
    
    game = Game(players, monsters, player_pos, monster_pos, grid)

    for game_num in range(trial_length):
        game.play_game(round_limit= round_limit)
    
    stats = {"difficulty": diff, "monsters": [monster.name for monster in monsters], "results": game.stat_log} 
     
    actions = {"difficulty": diff, "monsters": [monster.name for monster in monsters], "actions": game.turn_log} 

    stat_file = open("PlayTestingResults/stats_game-"+ name + ".txt", "w")
    stats_json = jsonpickle.encode(stats)
    stat_file.write(stats_json)

    turn_file = open("PlayTestingResults/turns_game-"+ name + ".txt", "w")
    turn_json = jsonpickle.encode(actions)
    turn_file.write(turn_json)

    stat_file.close() 
    turn_file.close() 

def manual_by_diff():
    diff_man = {"1/8": [], "1/4": [], "1/2": [], "1": []}
    for key in MONSTER_MANUAL:
        level = MONSTER_MANUAL[key]["level"]

        if level == 0.125:
            diff_man["1/8"].append(MONSTER_MANUAL[key])
        elif level == 0.25:
            diff_man["1/4"].append(MONSTER_MANUAL[key])
        elif level == 0.5:
            diff_man["1/2"].append(MONSTER_MANUAL[key])
        elif level == 1:
            diff_man["1"].append(MONSTER_MANUAL[key])
    
    return diff_man 



def create_random_encounter(difficulty, num_players):
    manual = manual_by_diff()
    xp_threshold = LEVEL_ONE_THES[difficulty] * num_players 

    possible_cr = ["1/8", "1/4", "1/2", "1"]
    unadjusted_xp = 0 
    xp_multiplier = 1
    monsters = []
    old_diff = xp_threshold

    while old_diff > 50 and len(possible_cr) >= 1:
        old_diff = abs((unadjusted_xp * xp_multiplier) - xp_threshold) 
        next_cr = random.choice(possible_cr) 

        new_xp = unadjusted_xp + CR_XP[next_cr]
        new_mult = num_mon_to_mult(len(monsters) + 1)
        new_dif = (new_xp * new_mult )- xp_threshold

        if abs(new_dif) < old_diff and new_dif < 50: 
             monsters.append(random.choice(manual[next_cr])) 
             unadjusted_xp = new_xp 
             xp_multiplier = num_mon_to_mult(len(monsters))
        else:
            # reduce the max CR if adding a monster makes
            # encounter too hard, reduce the max cr 
            possible_cr.pop()
    return monsters  



def random_trial_set_diff(name, agent_class, players, trial_length, difficulty, round_limit = 20, base_folder = "PlayTestingResults"):
    """
    Run a random encounter given a set of players 
    and a desired difficulty  
    """
    manual = manual_by_diff()
    
    # create random encounter 
    if difficulty in DIFF_TEMPS:
        temp = random.choice(DIFF_TEMPS[difficulty])
    else:
        raise Exception("Difficulty not found")
    
    monster_names = []
    monster_names += [random.choice(manual["1/8"]) for i in range(temp[0])]
    monster_names += [random.choice(manual["1/4"]) for i in range(temp[1])]
    monster_names += [random.choice(manual["1/2"]) for i in range(temp[2])]
    monster_names += [random.choice(manual["1"]) for i in range(temp[3])]

    monsters = [create_creature(agent_class,monster) for monster in monster_names]

    # Create game 
    diff = predict_difficuly(monsters)
    grid = Grid(7, 7)

    player_pos = []
    monster_pos = [] 
    for i in range(len(monsters)):
            monster_pos.append((0, i)) # monsters at top left 
    
    for i in range(len(players)): 
        player_pos.append((7 - 1, 7 - i - 1)) 
    
    game = Game(players, monsters, player_pos, monster_pos, grid)

    # run games 
    for game_num in range(trial_length):
        game.play_game(round_limit= round_limit)
    
    # save results to file 
    stats = {"difficulty": diff, "monsters": [monster.name for monster in monsters], "results": game.stat_log} 
     
    actions = {"difficulty": diff, "monsters": [monster.name for monster in monsters], "actions": game.turn_log} 

    stat_file = open(base_folder + "/stats_game-"+ name + ".txt", "w")
    stats_json = jsonpickle.encode(stats)
    stat_file.write(stats_json)

    turn_file = open(base_folder + "/turns_game-"+ name + ".txt", "w")
    turn_json = jsonpickle.encode(actions)
    turn_file.write(turn_json)

    stat_file.close() 
    turn_file.close() 

if __name__ == "__main__":
    # run random encounter on set party 
    player_names = ["orc warlock", "elf wizard", "human cleric", "tiefling ranger", "halfing ranger"]

    players = [create_creature(ProtectiveCreature, MANUAL[name]) for name in player_names]

    for i in range(20):
        print("Easy trial {}".format(i))
        random_trial_set_diff("easy-" + str(i), ProtectiveCreature, players, 15, "Easy", 20, base_folder = "TEST")

        print("Medium trial {}".format(i))
        random_trial_set_diff("medium-" + str(i),ProtectiveCreature, players, 15, "Medium", 20, base_folder = "TEST")

        print("Hard trial {}".format(i))
        random_trial_set_diff("hard-" + str(i),ProtectiveCreature, players, 15, "Hard", 20, base_folder = "TEST")

        print("Deadly trial {}".format(i))
        random_trial_set_diff("deadly-" + str(i), ProtectiveCreature, players, 15, "Deadly", 20,  base_folder = "TEST")


