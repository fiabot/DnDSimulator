from distutils.log import debug
from math import degrees
from tkinter.tix import MAIN
from DnDToolkit import * 
from BasicAgents import *  
from MonsterManual import *
from MonteCarloTreeSeaarch import MCTSCreature 
from ShyneAgent import * 
from JinJerryAgent import * 
from tournament import * 
from RuleBasedAgents import * 
import jsonpickle

# Timing tests 
"""jinParty, shyneParty = create_identical_parties(JinJerryCreature, ShyneCreature, MANUAL, 2)
map = Grid(10, 10, space = 3)
game = Game(jinParty, shyneParty,player_pos=[(9,9), (8,9)], monster_pos=[(0,0), (1,0)], map = map)
print(game.play_game(round_limit=10)) 

shyne_times = [c.average_time() for c in shyneParty]
shyne_avg = sum(shyne_times) / len(shyne_times)

jin_times = [c.average_time() for c in jinParty]
jin_avg = sum(jin_times) / len(jin_times)

print("Shyne average: {}, Jin average: {}".format(shyne_avg, jin_avg))"""

## Shyne Vs Random 
#print(tourament(ShyneCreature, RandomCreature, 2, MANUAL, round_limit= 20, debug=True))

## Shyne Vs JinJerry 
#print(tourament(ShyneCreature, JinJerryCreature, 10, MANUAL, round_limit= 20, debug=True))

## Shyne vs Aggressive 
#print(tourament(ShyneCreature, AggressiveCreature, 10, MANUAL, round_limit= 20, debug=True))


## Jin Jerry Vs Random
#print(tourament(JinJerryCreature, RandomCreature, 10, MANUAL, round_limit= 20, debug=True))

## Random vs Random 
#print(tourament(ShyneCreature, AggressiveCreature, 20, MANUAL, round_limit= 20, debug=True))

results = multi_agent_touranment([AggressiveCreature, ConversativeCreature, ProtectiveCreature, MCTSCreature, ShyneCreature, JinJerryCreature], 20, MANUAL, debug = True)

print(results)

pickled_results = jsonpickle.encode(results)
file = open("tourament_results.txt", "w")
file.write(pickled_results)