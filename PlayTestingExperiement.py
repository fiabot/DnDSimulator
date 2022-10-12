from DnDToolkit import *
from JinJerryAgent import JinJerryCreature 
from MonsterManual import *
from ShyneAgent import ShyneCreature 
import jsonpickle

"""
Randomly create 
play testing scenarios 
and records stats from play tests 

"""


def level_to_xp(level):
    if level == 0.125:
        return 25 
    elif level == 0.25:
        return 50 
    elif level == 0.5:
        return 100 
    else:
        return 200

def predict_difficuly(monsters):
    """
    return predicted difficulty 
    for 5 players 
    
    """

    crs = [level_to_xp(monster.level) for monster in monsters]
    total_xp = sum(crs)

    if len(monsters) == 2:
        total_xp *= 1.5
    elif len(monsters) > 2 and len(monsters) < 7:
        total_xp *= 2 
    elif len(monsters) > 7:
        total_xp *= 2.5 
    
    if total_xp < 187:
        return "Easy"
    elif total_xp < 312:
        return "Medium"
    elif total_xp < 438:
        return "Hard"
    else: 
        return "Deadly"



def play_random_games(name, agent_class, players, trial_length, round_limit = 20):
    length = random.randint(1, 5)
    monsters = create_random_party(agent_class, MONSTER_MANUAL, length)
    monsters = [monster for monster in monsters if not monster is None]
    diff = predict_difficuly(monsters)
    grid = Grid(7, 7)

    player_pos = []
    monster_pos = [] 
    for i in range(len(monsters)):
            monster_pos.append((0, i)) # monsters at top left 
    
    for i in range(len(players)): 
        player_pos.append((7 - 1, 7 - i - 1)) 
    
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

player_names = ["orc warlock", "elf wizard", "human cleric", "tiefling ranger", "halfing ranger"]

players = [create_creature(ShyneCreature, MANUAL[name]) for name in player_names]


for game in range(8, 50):
    print("Trial: {}".format(game))
    play_random_games(str(game), ShyneCreature, players, 30, 20)





