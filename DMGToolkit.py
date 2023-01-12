from statistics import mean
from MonsterManual import * 

LEVEL_ONE_THES = {"Easy": 25, "Medium": 50, "Hard": 75, "Deadly": 100}
CR_XP = {"1/8": 25, "1/4": 50, "1/2": 100, "1": 200}
DIFF_TEMPS = {"Easy": [(3,0,0,0), (1,1,0,0), (0,0,1,0)]}
DIFF_TEMPS["Medium"] = [(5,0,0,0), (3,1,0,0), (1,2,0,0), (0,1,1,0), (0,0,0,1)] 
DIFF_TEMPS["Hard"] = [(3,0,1,0), (1,1,1,0), (0,4,0,0), (1,3,0,0),(0, 1, 0, 1), (3,2,0,0)]
DIFF_TEMPS["Deadly"] = [(2,0,0,1), (2,0,2,0), (0,1,2,0), (0,5,0,0),(0,3,1,0)]

def names_to_chars(names):
    """
    look up name in 
    manual and return list 
    of stats 

    if name is not found, skip 
    """
    chars = [] 
    for name in names:
        name = name.lower()
        name = name.strip()
        if name in MANUAL:
            chars.append(MANUAL[name]) 
        else:
            raise Exception("Invalid Creature name: {}. Please use existing name".format(name.lower()))
    return chars 

def level_to_xp(level):
    if level == 0.125:
        return 25 
    elif level == 0.25:
        return 50 
    elif level == 0.5:
        return 100 
    else:
        return 200

def num_mon_to_mult(num_monsters):
    if num_monsters < 1:
        return 1 
    elif num_monsters == 2:
        return 1.5 
    elif num_monsters <= 6:
        return 2 
    elif num_monsters <= 10:
        return 2.5
    elif num_monsters <= 14:
        return 3
    else:
        return 3.5  

def get_adjusted_xp(monsters, just_names = False):
    """

    return adjusted xp 
    according to DMG given a set 
    of monsters 

    if monster list is just 
    monster names just names 
    will be true 
    """
    if (just_names):
      
        stats = names_to_chars(monsters)
        crs = [level_to_xp(monster["level"]) for monster in stats]
        
    else:
        crs = [level_to_xp(monster.level) for monster in monsters]
    total_xp = sum(crs)

    total_xp = total_xp * num_mon_to_mult(len(monsters))

    return total_xp 


def predict_difficuly(monsters, num_players = 5, just_names = False):
    """
    return predicted difficulty 
    for x players 
    
    """

    # find xp threshold for party 
    easy_thres= LEVEL_ONE_THES["Easy"] * num_players 
    med_thres= LEVEL_ONE_THES["Medium"] * num_players 
    hard_thres= LEVEL_ONE_THES["Hard"] * num_players 
    dead_thres= LEVEL_ONE_THES["Deadly"] * num_players 

    # find cut offs for what is considered what level 
    # this will be the average between it level and the next highest 
    easy_cutoff = mean([easy_thres, med_thres])
    med_cutoff = mean([med_thres, hard_thres])
    hard_cuttoff= mean([hard_thres, dead_thres])
    total_xp = get_adjusted_xp(monsters, just_names)
    
    if total_xp < easy_cutoff:
        return "Easy"
    elif total_xp < med_cutoff:
        return "Medium"
    elif total_xp < hard_cuttoff:
        return "Hard"
    else: 
        return "Deadly"