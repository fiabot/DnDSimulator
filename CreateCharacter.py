import json
from turtle import write_docstringdict
from Actions import Attack, MultiAttack, TwoHanded
from CreatureClasses import Modifiers
from DnDToolkit import *
from FeatureCatelog import ALL_FEATURES
from Features import FeatureManager
from SpellBook import SPELL_BOOK
from Spells import SpellManager 
import jsonpickle 

def make_attack():    
    if not input("Multiple attack ranges (y/n): ").lower().startswith("y"):
        name = input("attack name: ")
        hit = int(input("hit modifier: "))
        damage_dice = input("damage dice: ").lower() 
        damage_type = input("damage type: ").lower()
        dist = int(input("Attack range (in grid units): "))
        attack_type = input("Ranged or Melee: ").lower() 
        
        act = Attack(hit, damage_dice, dist, damage_type, name)
    else: 
        name = input("attack name: ")
        hit = int(input("hit modifier: "))
        close_dice = input("close range damage dice: ").lower() 
        wide_dice = input("wide range damage dice: ").lower() 
        damage_type = input("damage type: ").lower()
        short_dist = int(input("Close range distance(in grid units): "))
        long_dist = int(input("Wide range distance(in grid units): "))
        attack_type = input("Ranged or Melee: ").lower() 
    
        act = TwoHanded(hit, close_dice, wide_dice, short_dist, long_dist, attack_type, damage_type, name)
    
    return act 



def create_character():

    print("Tell us information about your character")

    name = input("name: ")
    level = int(input("level: "))
    hp = int(input("max hit points: "))
    speed = int(input("speed (in grid units): "))
    ac = int(input("Armor class: ")) 
    makes_saves = input("is player (y/n) ?").lower().startswith("y")
    mods = {DEX_STR: 1, CON_STR: 1, STR_STR: 0, CHAR_STR: 1, INT_STR: 0, WIS_STR: 0} 

    mods[DEX_STR] = int(input("Dexirity mod: "))
    mods[CON_STR] = int(input("Consititution mod: "))
    mods[STR_STR] = int(input("Strength mod: "))
    mods[CHAR_STR] = int(input("Charisma mod: "))
    mods[INT_STR] = int(input("Intelligence mod: "))
    mods[WIS_STR] = int(input("Wisdom mod: "))

    diff_save = input("input saving throws (y/n)?").lower().startswith("y")

    if diff_save: 
        save_mods = {DEX_STR: 1, CON_STR: 1, STR_STR: 0, CHAR_STR: 1, INT_STR: 0, WIS_STR: 0} 
        save_mods[DEX_STR] = int(input("Dexirity Saving mod: "))
        save_mods[CON_STR] = int(input("Consititution Saving mod: "))
        save_mods[STR_STR] = int(input("Strength Saving mod: "))
        save_mods[CHAR_STR] = int(input("Charisma Saving mod: "))
        save_mods[INT_STR] = int(input("Intelligence Saving mod: "))
        save_mods[WIS_STR] = int(input("Wisdom saving mod: "))
    
    else:
        save_mods = mods 
    
    init = int(input("Initative mod: "))

    modifers = Modifiers(init, mods, save_mods)

    has_resis = input("Input resistences (y/n)?").lower().startswith("y")
    resistences = [] 
    if has_resis:
        
        amount = int(input("number of resistences: "))
        for i in range(amount):
            resistences.append(input("enter resistence: ").lower())
    
    has_imm = input("Input immunities (y/n)?").lower().startswith("y")
    immunities = [] 
    if has_imm:
        
        amount = int(input("number of immunities: "))
        for i in range(amount):
            immunities.append(input("enter immunities: ").lower())
    
    con_immunities = [] 
    if has_imm:
        
        amount = int(input("number of condition immunities: "))
        for i in range(amount):
            con_immunities.append(input("enter condition immunities: ").lower())
    
    has_feats = input("input special features (y/n)?").lower().startswith("y")

    feats = [] 
    if has_feats: 
        amount = int(input("number of features: "))
        for i in range(amount):
            print("for feature {} of {}".format(i + 1, amount))
            feat = input("enter feature name: ").lower() 
            if feat in ALL_FEATURES:
                print("Feature is available")
            else:
                print("features {} is not available in this simulation".format(feat))
            feats.append(feat)
    

    num_acts = int(input("number of actions (not spells):"))
    acts = [] 

    for i in range(num_acts):
        print("for attack {} of {}".format(i + 1, num_acts))
        if input("is multi-attack (y/n):").lower().startswith("y"):
            mult_atts = [] 
            amount2 = int(input("Number of attacks in multiattack: "))
            for n in range(amount2):
                print("for sub-attack {} of {}".format(n + 1, amount2))
                mult_atts.append(make_attack())
            
            acts.append(MultiAttack(mult_atts))
        else:
            acts.append(make_attack())
    
    is_spell_caster = input("can cast spells (y/n)? ").lower().startswith("y")
    spell_man = {} 
    if is_spell_caster:
        spell_man["dc"] = int(input("spell casting dc: "))
        spell_man["attack mod"] = int(input("attack modifier: "))
        spell_man["spell mod"] = int(input("spell casting modifer: "))
        spell_man["spell slots"] = int(input("number of spell slots: "))

        num_spells = int(input("number of known spells: "))

        known_spells = [] 
        for i in range(num_spells):
            spell_name = input("spell name").lower() 
            if spell_name in SPELL_BOOK:
                known_spells.append(spell_name)
            else:
                print("The spell {} is not available in this simulation".format(spell_name))
                known_spells.append(spell_name)
        spell_man["known spells"] = known_spells
        
    else:
        spell_man = None 
    
    monster = {"ac":ac, "hp":hp, "speed": speed, "actions": acts, "name": name, 
                    "modifiers": modifers, "level": level, "resistances": resistences, 
                    "immunities": immunities, "features":feats, "spells": spell_man, 
                    "makes saves": makes_saves, "condition imun": con_immunities}
    return monster 

if __name__ == "__main__":
    read_files = open("player_files.txt")
    player_json = read_files.read() 
    read_files.close()

    if player_json != "":
        players = jsonpickle.decode(player_json)
    else:
        players = {}
    
    create_char = True 
    while create_char: 
        player = create_character()
        if player["name"] in players:
            overwrite = input("player {} already exists, overwrite? ".format(player["name"])).lower().startswith("y")
            if overwrite:
                players[player["name"]] = player 
        else:
            players[player["name"]] = player 

        create_char = input("create another character? ").lower().startswith("y")
    
        new_json = jsonpickle.encode(players)

        write_file = open("player_files.txt", "w")
        write_file.write(new_json)
        write_file.close() 




    



