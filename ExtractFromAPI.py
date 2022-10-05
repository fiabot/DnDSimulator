
from concurrent.futures.process import _chain_from_iterable_of_lists
from urllib import response
from FeatureCatelog import * 
import requests 
from CreatureClasses import * 
import json
from SpellBook import SPELL_BOOK
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

def get_two_dist(description):
    small_dist = 0 
    large_dist= 0 
    if description.find("reach") != -1:
        start = description.find("reach")
        feet = description[start + len("reach"): description.find("ft", start)]
        feet = feet.strip() 
        small_dist = math.ceil(int(feet) / 10)

    if description.find("range") != -1: 
        start = description.find("range")

        if description.find("/", start) != -1:
            feet =  description[description.find("/", start) + 1: description.find("ft", start)]
        else:
            feet = description[start + len("range"): description.find("ft", start)]
        feet = feet.strip() 
        try:
            large_dist = math.ceil(int(feet) / 10)
        except:
            print("Error finding distance within {}".format(description))
            print("Feed found {}".format(feet))
            large_dist = 0 
    
    return (small_dist, large_dist)

def make_spell_manager(description, char_json):
    print(description)
    dc_start = description.find("spell save DC ") + len("spell save DC ")
    dc_end = description.find(",", dc_start)
    if dc_end == -1:
        dc_end = description.find(")", dc_start)
    dc = int(description[dc_start: dc_end]) 
    
    mod_start = description.find("+")
    if mod_start != -1: 

        att_modifer = int(description[mod_start + 1: description.find(" ", mod_start)])
    else:
        att_modifer = 0 
    
    spell_slot_start = description.find("1st level (") + len("1st level (")
    if spell_slot_start != -1:
        spell_slots = description[spell_slot_start :description.find(" ", spell_slot_start)]
        spell_slots = int(spell_slots)
    else:
        spell_slots = 0 
    
    abl_start = description.find("spellcasting ability is ") + len("spellcasting ability is ")

    if abl_start != -1:
        ablilty = description[abl_start: description.find(" ", abl_start)].lower()
        spell_mod = score_to_mod(int(char_json[ablilty])) 
    else:
        spell_mod = 0 

    cantrips_start = description.find("Cantrips (at will): ") + len("Cantrips (at will): ")

    if cantrips_start != -1: 
        cantrip_str = description[cantrips_start: description.find("\n", cantrips_start)]
        cantrip_names = cantrip_str.split(", ")
    else: 
        cantrip_names = [] 

    spell_start = description.find("):", spell_slot_start) + len("): ")
    known_spells = [] 
    
    if spell_start != -1:
        spell_str = description[spell_start: description.find("\n", spell_start)]
        spell_names = spell_str.split(", ")

    found_all_spells = True 
    print(cantrip_names + spell_names)
    for spell in cantrip_names + spell_names:
        if spell in SPELL_BOOK:
            spell = spell.lower().strip() 
            print("{} was in the spell book".format(spell))
            known_spells.append(SPELL_BOOK[spell])
        else:
            print("{} was NOT in the spell book".format(spell)) 
            found_all_spells = False 
    spell_man = SpellManager(spell_slots, att_modifer, att_modifer, dc, known_spells, spell_mod)
    return spell_man, found_all_spells 
    





def make_two_ranged_weapon(act_json):
    small_damage_str = "0d4"
    large_damage_str = "0d4"
    hit = act_json["attack_bonus"]
    small_dist, large_dist = get_two_dist(act_json["desc"])
    name = act_json["name"]
    damage_type = act_json["damage"][0]["from"]["options"][0]["damage_type"]["name"].lower()  
    for damage_option in act_json["damage"][0]["from"]["options"]:
        if damage_option["notes"] == "One handed":
            small_damage_str = damage_option["damage_dice"]
        else:
            large_damage_str = damage_option["damage_dice"]
    return TwoHanded(hit, small_damage_str, large_damage_str, small_dist, large_dist, damage_type= damage_type, name = name)

def get_actions(li):
    actions = []
    multi_attacks = [] 
    multi_attack_choices = [] 
    is_impl = True 
    for act_json in li: 
        # is damage attack 
        if "attack_bonus" in act_json:
            attack = None 
            # normal attack damage 
            if "damage" in act_json and "damage_dice" in act_json["damage"][0]:
                hit = act_json["attack_bonus"]
                dist = get_dist(act_json["desc"])
                name = act_json["name"]
                damage_str = act_json["damage"][0]["damage_dice"]
                damage_type = act_json["damage"][0]["damage_type"]["name"].lower() 
                attack = Attack(hit, damage_str, dist, damage_type= damage_type, name = name)
            # different damage for range 
            elif "damage" in act_json and "choose" in act_json["damage"][0]: 
                attack = make_two_ranged_weapon(act_json)
            # other kind of attack 
            else:
                actions_list.append(act_json) 
                is_impl = False 

            
            actions.append(attack)
        
        # if multi attack 
        elif act_json["name"] == "Multiattack":
            attack_names = [] 
            # set amount of actions 
            if act_json["multiattack_type"] == 'actions':
                for action in act_json["actions"]:
                    if action["count"] == 1:
                        attack_names.append(action["action_name"])
                    elif isinstance(action["count"], str) and "d" in action["count"] :
                        roll = int(Dice(action["count"]).expected_value())
                        for i in range(roll):
                            attack_names.append(action["action_name"])
                    else:
                        amount = int(action["count"])
                        for i in range(amount):
                            attack_names.append(action["action_name"])
                multi_attacks.append(attack_names)
            # multiple choices 
            else: 
                choices = [] 
                for choice in act_json["action_options"]["from"]["options"]:
                    choice_names = [] 
                    if "items" in choice:
                        for attack in choice["items"]:
                            
                            if isinstance(attack["count"], int):
                                choice_names += ([attack["action_name"]] * attack["count"])
                            else:
                                choice_names.append(attack["action_name"])
                    else:
                        choice_names += ([choice["action_name"]] * choice["count"])
                    choices.append(choice_names)
                multi_attack_choices.append(choices) 
        # other kind of attack 
        else: 
            actions_list.append(act_json) 
            is_impl = False 
        
    # add any multi attacks 
    for mult_attack in multi_attacks:
        avail_attacks = []
        for name in mult_attack:
            act = [act for act in actions if act.name == name]
            if len(act) > 0:
                avail_attacks.append(act[0])
        action = MultiAttack(avail_attacks)
        # remove actions from list <-- alway does multiattack 
        #list(filter(lambda a: a.name in mult_attack, actions))
        actions.append(action) 
    
    # for multi attacks with choices, choose highest damage value 
    for choices in multi_attack_choices:
        choices_actions = [] 
        for choice in choices: 
            choice_actions = []
            for attack_name in choice: 
                choice_actions += [act for act in actions if act.name == attack_name]
            choices_actions.append(choice_actions)
        
        for acts in choices_actions:
            action = MultiAttack(acts)
            actions.append(action) 
            
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

def get_feats_and_spells(special_abil_li, char_json):
    spell_man = None
    features = [] 

    fully_imp = True

    for feat in special_abil_li:
        name = feat["name"].lower().strip() 
        if name in ALL_FEATURES: 
            features.append(ALL_FEATURES[name])
        elif name == "spellcasting":
            print("spell caster")
            spell_man, has_spell = make_spell_manager(feat["desc"], char_json)
            fully_imp = fully_imp and has_spell 
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
        feats, spell_man, is_impl2 = get_feats_and_spells(dict["special_abilities"], dict)
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

print("NUMBER FULLY IMPLEMENETED: ", (fully_impl))
print("PERCENT FULLY IMPLEMENETED: ", (fully_impl / len(chars)))



monster_json = jsonpickle.encode(chars)
write_features()

file = open("monster_manual.txt", "w")
file.write(monster_json)
file.close() 
