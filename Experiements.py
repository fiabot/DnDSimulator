
from DnDToolkit import * 
from BasicAgents import *  
from MonsterManual import *
from MonteCarloGameSearch import MonteCarloGameSearch
from MonteCarloTreeSeaarch import MCTSCreature
from OLETS import OLETSCreature 
from ShyneAgent import * 
from JinJerryAgent import * 
from tournament import * 
from RuleBasedAgents import * 
from RLAgent import * 
import jsonpickle

#print(tourament(RLCreature, AggressiveCreature, 4, PLAYER_MANUAL, round_limit= 4, debug = True))

manual_results = multi_agent_touranment([AggressiveCreature,  ProtectiveCreature, TrimmingCreature, MonteCarloGameSearch, OLETSCreature, JinJerryCreature],15, MANUAL, round_limit=20, debug=True) 

print(manual_results)

pickled_results = jsonpickle.encode(manual_results)
file = open("random_results.txt", "w")
file.write(pickled_results)
file.close()

player_results = multi_agent_touranment([AggressiveCreature,  ProtectiveCreature, TrimmingCreature, MonteCarloGameSearch, OLETSCreature, JinJerryCreature],15, PLAYER_MANUAL, round_limit=20, debug=True)

print(player_results)

pickled_results = jsonpickle.encode(player_results)
file = open("player_results.txt", "w")
file.write(pickled_results)
file.close() 
