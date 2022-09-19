
from DnDToolkit import * 
from BasicAgents import * 
from CreatureClasses import * 
#from JinJerryAgent import * 

# actions 
spear = Attack(2, "1d6", 6,  name = "spear")
bite = Attack(4, "1d4 + 2", 1, name = "bite")
scimitar = Attack(3, "1d6 + 1", 1, name = "scimitar")
shortsword = Attack(4, "1d6 + 2", 1, name ="shortsword")
shortbow = Attack(4, "1d6 + 2", 32, name = "shortbow")
ram = Attack(5, "1d6 +3", 1, name = "ram")
javelin = Attack(5, "1d6 + 3", 12, name = "javalin", attack_type= RANGED, damage_type= PIERCING_DAMAGE)
crossbow = Attack(3, "1d8 + 1", 32, name = "crossbow")
longbow = Attack(3, "1d8 + 1", 60,  name = "longbow")

prone_w_save = PARALYZED.add_end_of_turn(create_save_funct(CON_STR, 10))
claws = Attack(4, "2d4 + 2", 1, name = "claws", attack_type= MELE, damage_type= SLASHING_DAMAGE,
            side_effects= [SideEffect(prone_w_save, True, CON_STR, 10)] )

midbite = Attack(2, "2d6 + 2", 1, name = "bite")
greataxe = Attack(5, "1d12 + 3", 1, name = "greataxe", attack_type= MELE, damage_type= SLASHING_DAMAGE)

wolfbite = Attack(5, "2d6 + 3", 1, name = "bite", 
                    side_effects= [SideEffect(PRONE, True, STR_STR, 13)], attack_type=MELE, damage_type= PIERCING_DAMAGE)



# Monster Stats 

# 1/8 challenge 
bandit_mods = {DEX_STR: 1, CON_STR: 1, STR_STR: 0, CHAR_STR: 0, INT_STR: 0, WIS_STR: 0}
bandit = {"ac":12, "hp":11, "speed":3, "actions":[scimitar, crossbow], "name": "bandit", 
                                "modifiers": Modifiers(1, bandit_mods, bandit_mods)}

mer_mods = {DEX_STR: 1, CON_STR: 1, STR_STR: 0, CHAR_STR: 1, INT_STR: 0, WIS_STR: 0}
merfolk = {"ac":11, "hp":11, "speed":1, "actions":[spear], "name": "merfolf", 
                "modifiers": Modifiers(1, mer_mods, mer_mods)}

# 1/4 challenge 
elk_mods = {DEX_STR: 0, CON_STR: 1, STR_STR: 3, CHAR_STR: -2, INT_STR: -4, WIS_STR: 0}
elk = {"ac" :10 , "hp" : 13, "speed":5, "actions" : [ram], "name":"elk", "modifiers" : Modifiers(0, elk_mods, elk_mods), 
"features": FeatureManager([CHARGE])}

skel_mods = {DEX_STR: 2, CON_STR: 2, STR_STR: 0, CHAR_STR: -3, INT_STR: -4, WIS_STR: -2}
skeleton = {"ac":13, "hp":13, "speed":3 , "actions":[shortsword, shortbow], "name":"skeleton", 
        "modifiers": Modifiers(2, skel_mods, skel_mods), "features": FeatureManager(condition_immunities=[POSIONED.name])}
        

# 1/2 challenge 
orc_mods = {DEX_STR: 1, CON_STR: 3, STR_STR: 3, CHAR_STR: 0, INT_STR: -2, WIS_STR: 0}
orc = {"ac" :13 , "hp" : 15, "speed": 3,  "actions" : [greataxe, javelin], "name":"orc", 
            "modifiers": Modifiers(1, orc_mods, orc_mods)} # does not implement aggressive 

gnoll_mods = {DEX_STR: 1, CON_STR: 0, STR_STR: 2, CHAR_STR: -2, INT_STR: -2, WIS_STR: 0}
gnoll = {"ac":15, "hp":22, "speed":3, "actions":[bite, spear, longbow], "name":"gnoll",
                "modifiers": Modifiers(1, gnoll_mods, gnoll_mods), "features": FeatureManager([RAMPAGE])} # rampage slightly different


# 1 challenge 
wolf_mods = {DEX_STR: 2, CON_STR: 2, STR_STR: 3, CHAR_STR: -2, INT_STR: -4, WIS_STR: 1}
direWolf = {"ac":14, "hp":37, "speed": 5, "actions":[wolfbite], "name":"direwolf", 
                "modifiers": Modifiers(2, wolf_mods, wolf_mods), "features": FeatureManager([PACK_TACTICS])}

ghoul_mods = {DEX_STR: 2, CON_STR: 0, STR_STR: 1, CHAR_STR: -2, INT_STR: -2, WIS_STR: 0}
ghoul = {"ac":12, "hp":22, "speed":3, "actions":[midbite, claws], "name":"ghoul", 
                "modifiers": Modifiers(2, ghoul_mods, ghoul_mods), "features" : FeatureManager(condition_immunities= [POSIONED.name])}

def create_creature(agent_class, creat_dict):
    """
    create a new creature given a base class 
    and a monster dict
    """
    if "features" in creat_dict:
        features = creat_dict["features"]
    else: 
        features = FeatureManager() 
    monster = agent_class(ac = creat_dict["ac"], hp = creat_dict["hp"],
            speed = creat_dict["speed"], actions = creat_dict["actions"], name = creat_dict["name"], 
            modifiers = creat_dict["modifiers"], features = features)
    
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


