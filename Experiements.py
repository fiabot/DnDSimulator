from distutils.log import debug
from math import degrees
from tkinter.tix import MAIN
from DnDToolkit import * 
from BasicAgents import *  
from MonsterManual import *
from MonteCarloGameSearch import MonteCarloGameSearch
from MonteCarloTreeSeaarch import MCTSCreature 
from ShyneAgent import * 
from JinJerryAgent import * 
from tournament import * 
from RuleBasedAgents import * 
import jsonpickle

print(tourament(AggressiveCreature, ProtectiveCreature2, 100, PLAYER_MANUAL, round_limit= 50))

#results = multi_agent_touranment([AggressiveCreature, ConversativeCreature, ProtectiveCreature, MCTSCreature, ShyneCreature, JinJerryCreature],20, MANUAL, round_limit=20, debug=True) 

#print(results)

#pickled_results = jsonpickle.encode(results)
#file = open("tourament_results.txt", "w")
#file.write(pickled_results)