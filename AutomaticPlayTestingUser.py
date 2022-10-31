from DnDToolkit import *
from JinJerryAgent import JinJerryCreature 
from MonsterManual import *
from ShyneAgent import ShyneCreature 
from RuleBasedAgents import * 

# choose agent 
print("Choose agent from: \n\t1. Agressive \n\t2. JinJerry \n\t3. ShyneAgent")

agent_num = int(input("Make a selection: "))

if agent_num == 1:
    agent = AggressiveCreature 
elif agent_num == 2: 
    agent = JinJerryCreature 
else:
    agent = ShyneCreature 

manual = create_manual(agent, MANUAL)
# get player list 
players= []

print("Build the PLAYER team: ")

enter_more = True

while enter_more and len(players) < 5:
    player_name = input("Enter character name or enter 'quit': ")
    if player_name.lower() == "quit":
        enter_more = False 
    else:
        if player_name in manual:
            print("Added {} to player team".format(player_name))
            players.append(deepcopy(manual[player_name]))
        else:
            print("Creature {} was not found, please add creature first")



monsters = []



print("Build the MONTER team: ")

enter_more = True

while enter_more and len(monsters) < 5:
    player_name = input("Enter character name or enter 'quit': ")
    if player_name.lower() == "quit":
        enter_more = False 
    else:
        if player_name in manual:
            print("Added {} to mosnter team".format(player_name))
            monsters.append(deepcopy(manual[player_name]))
        else:
            print("Creature {} was not found, please add creature first")

map_width = int(input("Width of the map: "))
map_height = int(input("Height of the map: "))
map = Grid(map_height, map_width)

player_pos = []
monster_pos = [] 
if input("Mannually input positions (y/n)?").lower().startswith("y"):
    
    for player in players:
        x = int(input("starting x pos for {}".format(player.name)))
        y = int(input("starting y pos for {}".format(player.name)))
        player_pos.append((y,x))
    
    for player in monsters:
        x = int(input("starting x pos for {}".format(player.name)))
        y = int(input("starting y pos for {}".format(player.name)))
        monster_pos.append((y,x))
else:
    for i in range(len(monsters)):
            monster_pos.append((0, i)) # monsters at top left 
    
    for i in range(len(players)): 
        player_pos.append((map_height - 1, map_width - i - 1)) # players at bottom right 

# ensure that names are unqiue
make_unqiue(players + monsters) 
print(", ".join([player.name for player in players]))
print(", ".join([player.name for player in monsters]))


game = Game(players, monsters, player_pos, monster_pos, map)

num_games = int(input("number of games: "))
round_limit = int(input("round limit: "))

results = {PLAYERTEAM:0, MONSTERTEAM:0, TIE:0, INCOMPLETE:0}
for game_num in range(num_games):
    winner = game.play_game(round_limit= round_limit)
    results[winner[0]] += 1 
    print(results)
print(game.get_average_stats())
print(game.stat_log)

