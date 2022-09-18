from DnDToolkit import * 
from BasicAgents import * 
from CreatureClasses import * 
#from JinJerryAgent import * 

# actions 
spear = Attack(2, "1d6", 6,  name = "spear")
bite = Attack(4, "1d4 + 2", 1, name = "bite")
scimitar = Attack(3, "1d6 + 1", 1, name = "scimitar")
shortsword = Attack(4, "1d6 + 2", 1, name ="shortsword")
shortbow = Attack(4, "1d6 + 2", 32, min_dist= 8, name = "shortbow")
ram = Attack(5, "1d6 +3", 1, name = "ram")
javelin = Attack(5, "1d6 + 3", 12, min_dist=3, name = "javalin")
crossbow = Attack(3, "1d8 + 1", 32, min_dist= 8, name = "crossbow")
longbow = Attack(3, "1d8 + 1", 60, min_dist=15,  name = "longbow")
claws = Attack(4, "2d4 + 2", 1, name = "claws")
midbite = Attack(2, "2d6 + 2", 1, name = "medium bite")
greataxe = Attack(5, "1d12 + 3", 1, name = "greataxe")
bigbite = Attack(5, "2d6 + 3", 1, name = "big bite")



# Monster Stats 

# 1/8 challenge 
bandit_mods = {DEX_STR: 1, CON_STR: 1, STR_STR: 0, CHAR_STR: 0, INT_STR: 0, WIS_STR: 0}
bandit = {"ac":12, "hp":11, "speed":3, "actions":[scimitar, crossbow], "name": "bandit", 
                                "modifers": Modifiers(1, bandit_mods, bandit_mods)}

mer_mods = {DEX_STR: 1, CON_STR: 1, STR_STR: 0, CHAR_STR: 1, INT_STR: 0, WIS_STR: 0}
merfolk = {"ac":11, "hp":11, "speed":1, "actions":[spear], "name": "merfolf", 
                "modifiers": Modifiers(1, mer_mods, mer_mods)}

# 1/4 challenge 
elk_mods = {DEX_STR: 0, CON_STR: 1, STR_STR: 3, CHAR_STR: -2, INT_STR: -4, WIS_STR: 0}
elk = {"ac" :10 , "hp" : 13, "speed":5, "actions" : [ram], "name":"elk", "modifiers" : Modifiers(0, elk_mods, elk_mods)}

skeleton = {"ac":13, "hp":13, "speed":3 , "actions":[shortsword, shortbow], "name":"skeleton"}

# 1/2 challenge 
orc = {"ac" :13 , "hp" : 15, "speed": 3,  "actions" : [greataxe, javelin], "name":"orc"}
gnoll = {"ac":15, "hp":22, "speed":3, "actions":[bite, spear, longbow], "name":"gnoll"}

# 1 challenge 
direWolf = {"ac":14, "hp":37, "speed": 5, "actions":[bigbite], "name":"direwolf"}
ghoul = {"ac":12, "hp":22, "speed":3, "actions":[midbite, claws], "name":"ghoul"}

def create_creature(agent_class, creat_dict):
    """
    create a new creature given a base class 
    and a monster dict
    """
    monster = agent_class(ac = creat_dict["ac"], hp = creat_dict["hp"],
            speed = creat_dict["speed"], actions = creat_dict["actions"], name = creat_dict["name"])
    
    return monster 


def create_manual(agent_class, creature_dicts):
    """
    return a list of 
    creatures of a given class 
    and given dictionary of stats 
    """
    manual = [] 

    for dict in creature_dicts:
        manual.append(create_creature(agent_class, dict))
    
    return manual 

def create_party(agent_class, manual, size):
    """
    create a random party given a
    manual, agent class, and party size  
    """

    party = [] 

    for i in range(size):
        creature = random.choice(manual)
        party.append(create_creature(agent_class, creature))
    
    return party 

def create_identical_parties(agent_class1, agent_class2, manual, size):
    party1 = [] 
    party2 = [] 

    for i in range(size):
        creature = random.choice(manual)
        party1.append(create_creature(agent_class1, creature))
        party2.append(create_creature(agent_class2, creature))
    
    return party1, party2 
MANUAL = [bandit, merfolk, elk, skeleton, orc, gnoll, direWolf, ghoul]
if __name__ == "__main__":
    #jinjerry_manual = create_manual(JinJerryCreature, MANUAL)
    random_manual = create_manual(RandomCreature, MANUAL)


