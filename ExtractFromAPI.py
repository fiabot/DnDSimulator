
from concurrent.futures.process import _chain_from_iterable_of_lists
from urllib import response
from FeatureCatelog import * 
import requests 
from CreatureClasses import * 
import json
from Spells import SpellManager 
import jsonpickle


reponse = requests.get("https://www.dnd5eapi.co/api/monsters/bandit")

feature_list = {}
actions_list = []

monster_dict = json.loads(reponse.text)

def get_speed(speed_str):
    speed = int(speed_str[:speed_str.find(" ")])
    return math.ceil(speed / 10) 

def get_dist(description):
    if description.find("reach") != -1:
        start = description.find("reach")
        feet = description[start + len("reach"): description.find("ft", start)]
        feet = feet.strip() 
        return math.ceil(int(feet) / 10)

    elif description.find("range") != -1: 
        start = description.find("range")

        if description.find("/", start) != -1:
            feet =  description[description.find("/", start) + 1: description.find("ft", start)]
        else:
            feet = description[start + len("range"): description.find("ft", start)]
        feet = feet.strip() 
        try:
            return math.ceil(int(feet) / 10)
        except:
            print("Error finding distance within {}".format(description))
            print("Feed found {}".format(feet))
            return 0 
    else:
        print("can't find")

def get_actions(li):
    actions = []
    is_impl = True 
    for act_json in li: 
        if "attack_bonus" in act_json:
            hit = act_json["attack_bonus"]
            if "damage" in act_json and "damage_dice" in act_json["damage"][0]:
                damage_str = act_json["damage"][0]["damage_dice"]
                damage_type = act_json["damage"][0]["damage_type"]["name"].lower() 
            elif "damage" in act_json and "choose" in act_json["damage"][0]: 
                damage_str = act_json["damage"][0]["from"]["options"][0]["damage_dice"]
                damage_type = act_json["damage"][0]["from"]["options"][0]["damage_type"]["name"].lower() 
                actions_list.append(act_json) 
                is_impl = False 
            else:
                damage_str = "0d0"
                damage_type = SLASHING_DAMAGE
                actions_list.append(act_json) 
                is_impl = False 
            dist = get_dist(act_json["desc"])
            name = act_json["name"]
            attack = Attack(hit, damage_str, dist, damage_type= damage_type, name = name)
            actions.append(attack)
            
        else: 
            actions_list.append(act_json) 
            is_impl = False 
    return actions, is_impl 

def score_to_mod(score):
    """

    turn a ability score into it's 
    modifer 
    
    """
    return math.floor((score - 10) / 2)

def get_mods(dict):
    """
    create a modifer object 
    from a character dictionary
    """
    mods = {DEX_STR: 0, CON_STR: 0, STR_STR: 0, CHAR_STR: 0, INT_STR: 0, WIS_STR: 0}

    if "dexterity" in dict:
        mods[DEX_STR] = score_to_mod(dict["dexterity"]) 

    if "strength" in dict:
        mods[STR_STR] = score_to_mod(dict["strength"])

    if "charisma" in dict:
        mods[CHAR_STR] = score_to_mod(dict["charisma"])
    
    if "intelligence" in dict:
        mods[INT_STR] = score_to_mod(dict["intelligence"])
    
    if "wisdom" in dict:
        mods[WIS_STR] = score_to_mod(dict["wisdom"])
    
    return Modifiers(mods[DEX_STR], mods, mods)

def lower_list(list):
    return (s.lower() for s in list)

def get_feats_and_spells(special_abil_li):
    spell_man = None
    features = [] 

    fully_imp = True

    for feat in special_abil_li:
        name = feat["name"].lower().strip() 
        if name in ALL_FEATURES: 
            features.append(ALL_FEATURES[name])
        else: 
            fully_imp = False
            feature_list[feat["name"]] = feat["desc"] 
    
    return features, spell_man, fully_imp 



def json_to_char(dict):
    name = dict["name"]
    ac = dict["armor_class"]
    hit_points  = dict["hit_points"]
    

    if "speed" in dict and "walk" in dict["speed"]:
        speed = get_speed(dict["speed"]["walk"]) 
    else:
        speed = 0

    actions, is_impl1 = get_actions(dict["actions"])
    challenge_rating = float(dict["challenge_rating"]) 
    #monster = Creature(ac = ac, hp = hit_points, speed = speed, name = name, actions = actions)
    immunities = lower_list(dict["damage_immunities"]) 
    resistences = lower_list(dict["damage_resistances"])

    if "special_abilities" in dict:
        feats, spell_man, is_impl2 = get_feats_and_spells(dict["special_abilities"])
        feat_manager = FeatureManager(feats, dict["condition_immunities"])
    else: 
        feat_manager = FeatureManager([], dict["condition_immunities"])
        spell_man = None 
        is_impl2 = True 

    mods = get_mods(dict)
    monster = {"ac":ac, "hp":hit_points, "speed": speed, "actions": actions, "name": name, 
                    "modifiers": mods, "level": challenge_rating, "resistances": resistences, 
                    "immunities": immunities, "features":feat_manager, "spells": spell_man, 
                    "fully_impl": is_impl1 and is_impl2}
    return monster 

def get_all_from_level(level):
    res = requests.get("https://www.dnd5eapi.co/api/monsters?challenge_rating={}".format(level))
    print("Number of creatures:{}".format(json.loads(res.text)["count"])) 
    monster_list = json.loads(res.text)["results"]

    characters = {}
    for monster in monster_list:
        url = "https://www.dnd5eapi.co" + monster["url"]
        json_dict = json.loads(requests.get(url).text)
        print(json_dict["name"])
        char_dict = json_to_char(json_dict)
        
        characters[char_dict["name"]] = char_dict
    return characters 

def write_features():
    file = open("feats_to_impl.txt", "w")

    for key in feature_list:
        file.write("{} : {} \n\n".format(key, feature_list[key]))


    file.close() 

    file = open("acts_to_impl.txt", "w")

    for act in actions_list:
        file.write("{} : {}\n\n".format(act["name"], act))

    file.close() 



print("1/8 level creatures:")
chars = get_all_from_level(0.125)

print("1/4 level creatures:")
chars.update(get_all_from_level(0.25))

print("1/2 level creatures:")
chars.update(get_all_from_level(0.5)) 

print("1 level creatures:")
chars.update(get_all_from_level(1)) 


fully_impl = 0 

for name in chars:
    if chars[name]["fully_impl"]:
        fully_impl += 1 

print("PERCENT FULLY IMPLEMENETED: ", (fully_impl / len(chars)))



monster_json = jsonpickle.encode(chars)
write_features()

file = open("monster_manual.txt", "w")
file.write(monster_json)