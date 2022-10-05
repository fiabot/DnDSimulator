
from FeatureCatelog import ALL_FEATURES
from SpellBook import SPELL_BOOK
from Spells import SpellManager
import jsonpickle

from BasicAgents import *
from CreatureClasses import *
from DnDToolkit import *

#from JinJerryAgent import * 

# actions 
"""spear = Attack(2, "1d6", 6,  name = "spear")
bite = Attack(4, "1d4 + 2", 1, name = "bite")
scimitar = Attack(3, "1d6 + 1", 1, name = "scimitar")
shortsword = Attack(4, "1d6 + 2", 1, name ="shortsword")
shortbow = Attack(4, "1d6 + 2", 32, name = "shortbow")
ram = Attack(5, "1d6 +3", 1, name = "ram")
javelin = Attack(5, "1d6 + 3", 12, name = "javalin", attack_type= RANGED, damage_type= PIERCING_DAMAGE)
crossbow = Attack(3, "1d8 + 1", 32, name = "crossbow")
longbow = Attack(3, "1d8 + 1", 60,  name = "longbow")

par_w_save = PARALYZED.add_end_of_turn(create_save_funct(CON_STR, 10))
claws = Attack(4, "2d4 + 2", 1, name = "claws", attack_type= MELE, damage_type= SLASHING_DAMAGE,
            side_effects= [SideEffect(par_w_save, True, CON_STR, 10)] )

midbite = Attack(2, "2d6 + 2", 1, name = "bite")
greataxe = Attack(5, "1d12 + 3", 1, name = "greataxe", attack_type= MELE, damage_type= SLASHING_DAMAGE)

wolfbite = Attack(5, "2d6 + 3", 1, name = "bite", 
                    side_effects= [SideEffect(PRONE, True, STR_STR, 13)], attack_type=MELE, damage_type= PIERCING_DAMAGE)



# Monster Stats 

# 1/8 challenge 
bandit_mods = {DEX_STR: 1, CON_STR: 1, STR_STR: 0, CHAR_STR: 0, INT_STR: 0, WIS_STR: 0}
bandit = {"ac":12, "hp":11, "speed":3, "actions":[scimitar, crossbow], "name": "bandit", 
                                "modifiers": Modifiers(1, bandit_mods, bandit_mods), "level": 0.125}

mer_mods = {DEX_STR: 1, CON_STR: 1, STR_STR: 0, CHAR_STR: 1, INT_STR: 0, WIS_STR: 0}
merfolk = {"ac":11, "hp":11, "speed":1, "actions":[spear], "name": "merfolk", 
                "modifiers": Modifiers(1, mer_mods, mer_mods), "level": 0.125}

# 1/4 challenge 
elk_mods = {DEX_STR: 0, CON_STR: 1, STR_STR: 3, CHAR_STR: -2, INT_STR: -4, WIS_STR: 0}
elk = {"ac" :10 , "hp" : 13, "speed":5, "actions" : [ram], "name":"elk", "modifiers" : Modifiers(0, elk_mods, elk_mods), 
"features": FeatureManager([CHARGE]), "level": 0.25}

skel_mods = {DEX_STR: 2, CON_STR: 2, STR_STR: 0, CHAR_STR: -3, INT_STR: -4, WIS_STR: -2}
skeleton = {"ac":13, "hp":13, "speed":3 , "actions":[shortsword, shortbow], "name":"skeleton", 
        "modifiers": Modifiers(2, skel_mods, skel_mods), "features": FeatureManager(condition_immunities=[POSIONED.name]), 
        "level": 0.25}
        

# 1/2 challenge 
orc_mods = {DEX_STR: 1, CON_STR: 3, STR_STR: 3, CHAR_STR: 0, INT_STR: -2, WIS_STR: 0}
orc = {"ac" :13 , "hp" : 15, "speed": 3,  "actions" : [greataxe, javelin], "name":"orc", 
            "modifiers": Modifiers(1, orc_mods, orc_mods), "level": 0.5} # does not implement aggressive 

gnoll_mods = {DEX_STR: 1, CON_STR: 0, STR_STR: 2, CHAR_STR: -2, INT_STR: -2, WIS_STR: 0}
gnoll = {"ac":15, "hp":22, "speed":3, "actions":[bite, spear, longbow], "name":"gnoll",
                "modifiers": Modifiers(1, gnoll_mods, gnoll_mods), "features": FeatureManager([RAMPAGE]), 
                "level": 0.5} # rampage slightly different


# 1 challenge 
wolf_mods = {DEX_STR: 2, CON_STR: 2, STR_STR: 3, CHAR_STR: -2, INT_STR: -4, WIS_STR: 1}
direWolf = {"ac":14, "hp":37, "speed": 5, "actions":[wolfbite], "name":"direwolf", 
                "modifiers": Modifiers(2, wolf_mods, wolf_mods), "features": FeatureManager([PACK_TACTICS]), "level": 1}

ghoul_mods = {DEX_STR: 2, CON_STR: 0, STR_STR: 1, CHAR_STR: -2, INT_STR: -2, WIS_STR: 0}
ghoul = {"ac":12, "hp":22, "speed":3, "actions":[midbite, claws], "name":"ghoul", 
                "modifiers": Modifiers(2, ghoul_mods, ghoul_mods), 
                "features" : FeatureManager(condition_immunities= [POSIONED.name]), "level": 1}"""

def create_creature(agent_class, creat_dict):
    """
    create a new creature given a base class 
    and a monster dict
    """
    if "features" in creat_dict:
        features_list = [] 
        for feat in creat_dict["features"]:
            if feat.lower() in ALL_FEATURES:
                features_list.append(ALL_FEATURES[feat.lower()])
        features = FeatureManager([], creat_dict["condition imun"]) 
    else: 
        features = FeatureManager([], creat_dict["condition imun"]) 

    if "immunities" in creat_dict:
        immunites = creat_dict["immunities"]
    else:
        immunites = [] 
    
    if "resistences" in creat_dict:
        resis = creat_dict["resistences"]
    else: 
        resis = [] 
    
    if "makes saves" in creat_dict:
        makes_saves = creat_dict["makes saves"]
    else:
        makes_saves = False 
    
    if "spells" in creat_dict and not creat_dict["spells"] is None:
        spell_dict = creat_dict["spells"]
        dc = spell_dict["dc"]
        att_mod = spell_dict["attack mod"]
        spell_mod = spell_dict["spell mod"]
        spell_slot = spell_dict["spell slots"]

        spells = []
        for spell in spell_dict["known spells"]:
            if spell in SPELL_BOOK:
                spells.append(SPELL_BOOK[spell])
        
        spell_manager= SpellManager(spell_slot, att_mod, att_mod, dc, spells, spell_mod)
    else:
        spell_manager = None 

    monster = agent_class(ac = creat_dict["ac"], hp = creat_dict["hp"],
            speed = creat_dict["speed"], actions = creat_dict["actions"], name = creat_dict["name"], 
            modifiers = creat_dict["modifiers"], features = features, level = creat_dict["level"], 
            immunities = immunites, resistences = resis, makes_death_saves = makes_saves, spell_manager = spell_manager )
    
    return monster 


def create_manual(agent_class, creature_dicts):
    """
    return a list of 
    creatures of a given class 
    and given dictionary of stats 
    """
    manual = {}

    for key in creature_dicts:
        manual[key] = create_creature(agent_class, creature_dicts[key])
    
    return manual 

def create_random_party(agent_class, manual, size):
    """
    create a random party given a
    manual, agent class, and party size  
    """

    party = [] 

    for i in range(size):
        creature = random.choice(list( manual.values()))
        party.append(create_creature(agent_class, creature))
    
    return party 

def create_random_identical_parties(agent_class1, agent_class2, manual, size):
    party1 = [] 
    party2 = [] 

    for i in range(size):
        creature = random.choice(list( manual.values()))
        party1.append(create_creature(agent_class1, creature))
        party2.append(create_creature(agent_class2, creature))
    
    return party1, party2 

monster_man_file = open("monster_manual.txt", "r")
monster_json = monster_man_file.read() 
monster_man_file.close()


player_man_file = open("player_files.txt", "r")
player_json = player_man_file.read() 
player_man_file.close()
MANUAL = jsonpickle.decode(monster_json)
MANUAL.update(jsonpickle.decode(player_json))
#MANUAL.update(jsonpickle.decode(player_json))

if __name__ == "__main__":
    #jinjerry_manual = create_manual(JinJerryCreature, MANUAL)
    random_manual = create_manual(RandomCreature, MANUAL)

    for key in random_manual:
        print("Creature: {}, ac: {}, hp:{}".format(key, random_manual[key].ac, random_manual[key].hp))

        for action in  random_manual[key].actions:
            if isinstance(action, Attack) or isinstance(action, TwoHanded):
                if isinstance(action.dist, str):
                    print("CREATURE: {} has problem with attack:{} with value {}".format(key, action.name, action.dist))




