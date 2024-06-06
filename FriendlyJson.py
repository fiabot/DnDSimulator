from MonsterManual import MONSTER_MANUAL , PLAYER_MANUAL, MANUAL 
from SpellBook import SPELL_BOOK 
from FeatureCatelog import ALL_FEATURES
from copy import deepcopy

def nice_json(bad_json):
    new_json = deepcopy(bad_json)
    new_json["actions"] = [{"name": action.name, "desc": action.desc()} for action in new_json["actions"]]
    mods = new_json["modifiers"]
    new_json["speed"] = new_json["speed"] * 10 
    new_json["initiative"] = mods.initative 
    new_json["modifiers"] = mods.skill_mods
    new_json["save_modifiers"] = mods.save_mods
    new_json["resistances"] = list(new_json["resistances"])
    new_json["immunities"] = list(new_json["immunities"])
    

    feats = []
    for feat in bad_json["features"]:
        di = {"name": feat}
        if feat in ALL_FEATURES:
            di["desc"] = ALL_FEATURES[feat].desc 
            print(ALL_FEATURES[feat].desc)
        else:
            di["desc"] = "Not implemented"
        
        feats.append(di)
    
    new_json["features"] = feats 
    if (new_json["spells"] != None):
        all_spells = new_json["spells"]['known spells']
        first_level = [spell for spell in all_spells if spell in SPELL_BOOK and SPELL_BOOK[spell].level == 1]
        cantrip = [spell for spell in all_spells if spell in SPELL_BOOK and SPELL_BOOK[spell].level == 0]
        un_impl = [spell for spell in all_spells if not spell in SPELL_BOOK ]
        new_json["spells"]['known spells'] = {"firsts": first_level, "cantrips": cantrip, "un_impl": un_impl}
    return new_json



if __name__ == "__main__":
    print(nice_json(MANUAL["human fighter"]))
