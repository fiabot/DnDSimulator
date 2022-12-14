
from Features import *
from Conditions import * 
from DnDToolkit import * 
"""
All currently implemented features 

"""
def friend_in_range(attack, attacker, game):
    """
    Return true if there is an ally 
    1 tile from creature 
    """
    tiles = game.map.tiles_in_range(attacker.position, 1, 1)

    found_friend = False 
    i = 0 
    while not found_friend and i < len(tiles):
        tile = tiles[i]
        if not tile is None: 
            try: 
                found_friend = tile[0].team == attacker.team
            except: 
                pass 
        i += 1 
    
    return found_friend 
def friend_non_incapac(attack, attacker, game):
    tiles = game.map.tiles_in_range(attacker.position, 1, 1)

    found_friend = False 
    i = 0 
    while not found_friend and i < len(tiles):
        tile = tiles[i]
        if not tile is None: 
            try: 
                found_friend = (tile[0].team == attacker.team) and (not tile[0].has_condition(INCAPACITATED.name))
            except: 
                pass 
        i += 1 
damage_is_true = lambda attack, attacker, game: True   

wisd = lambda type : type == WIS_STR 
charm_fright = lambda type, effect, is_magic = False: effect == "charmed" or effect == "frightened"
has_relent = lambda amount, creature, game: not "Relentless Endurance" in creature.game_data 
prone_saving = lambda type, effect, is_magic = False: (type == DEX_STR or type == STR_STR) and effect == PRONE.name
is_char = lambda type, effect, is_magic =False: effect == "charmed" 
death_is_true = lambda amount, creature, game : True
fortitude_condition = lambda amount, creature, game: creature.saving_throw(CON_STR, "Undead Fortitude") > 5 + amount 
can_use_gnome_cun = lambda type, effect, is_magic = False: effect == "magic" and (type == WIS_STR or type == INT_STR or type == CHAR_STR)
can_use_two_header = lambda type, effect, is_magic = False: type == WIS_STR.name 
can_use_drug = lambda type, effect, is_magic = False: effect == POSIONED.name or effect == PARALYZED.name or effect == "magic"
is_fright = lambda type, effect, is_magic = False: effect == "frightened"
can_cunning = lambda type, effect, is_magic = False: is_magic and (type == WIS_STR or type == CHAR_STR or type == INT_STR)
is_magic = lambda type, effect, is_magic = False: is_magic 
def create_damage_less_than(value):
    def foo(amount, creature, game):
        return amount < value

def can_rampage(amount, creature, game):
    return game.map.distance(game.map.closest_enemy(creature.team, creature.position).position, creature.position) <= 1


# effects 
def use_relent(amount, creature, game):
    creature.game_data["Relentless Endurance"] = 1 
    if creature.hp == 0:
        creature.hp = 1 

def get_one_hp(amount, creature, game):
    if creature.hp == 0:
        creature.hp = 1 
def bonus_damage (dice_string):
    def damage_added (attack,attacker, game):
        return Dice(dice_string).roll() 
    return damage_added 

def one_more_dice(attack, attacker, game):
    if not attack.hit_dice is None: 
        dice = Dice(make_dice_string(1, attack.hit_dice.type, 0))
        return dice.roll() 
    else:
        return 0

def create_does_charge(dist):
    def does_charge(attack, attacker, game): 
        return game.map.distance(attacker.position, attacker.last_pos) >= dist
    return does_charge 

def charge_damage(dice_string, save_type, save_dc):
    def charge_damage(attack, attacker, game):
        is_prone = attacker.saving_throw(save_type, PRONE.name) >= save_dc
        if is_prone: 
            game.get_creature(attack.target).add_condition(PRONE)
        
        return Dice(dice_string).roll() 
    return charge_damage


def rampage(amount, creature, game): 
    bite = None 
    i = 0 
    while bite is None and i < len(creature.actions):
        act = creature.actions[i]
        if act.name == "bite":
            bite = act
        i += 1 
    if not bite is None: 
        bite_copy = deepcopy(bite)
        bite_copy.target = game.map.closest_enemy(creature.team, creature.position).name 
        bite_copy.attacker = creature.name 
        bite.execute(game) 

def death_burst_fun(amount, creature, game):
    for piece in game.map.pieces_in_range(creature.position, 1):
        roll = Dice("2d6").roll() 
        if piece.saving_throw(DEX_STR, FIRE_DAMAGE) >= 11:
            piece.damage(roll, FIRE_DAMAGE)
        else:
            piece.damage(roll // 2, FIRE_DAMAGE)

def re_roll_below(re_roll_value):
    def foo (hit, dice, attack, attacker, game):
        nat_hit = hit - dice.modifer 
        if nat_hit <= re_roll_value:
            return dice.roll() 
        else:
            return hit 
    return foo 

def savage(hit, dice, attack, attacker, game):
    nat_hit = hit - dice.modifer 
    if nat_hit == 20:
        target = game.get_creature(attack.target)
        if not target is None: 
            damage = Dice(make_dice_string(1, attack.damage_dice.type, 0)).roll() 
            target.damage(damage, attack.damage_type, game)
    
    return hit 

SNEAK_ATTACK = DamageFeature("sneak attack", friend_in_range, bonus_damage("2d6"))
DARK_DEVOTION = SavingThrowFeature("dark devotion", charm_fright, 1, 0) 
WISDOM_ADV = SkillCheckFeature("keen sight", wisd, 1 , 20)
RELENTLESS_ENDUR = DeathFeature("relentless endurance", has_relent, use_relent)
CHARGE = DamageFeature("charge", create_does_charge(2), charge_damage("2d6",  STR_STR, 13))
RAMPAGE = DeathFeature("rampage", can_rampage, rampage) 
PACK_TACTICS = AttackFeature("pack tactics", friend_in_range, 1, 0)
RELENTLESS = DeathFeature("relentless", create_damage_less_than(7), get_one_hp)
TRAMPLING_CHARGE = DamageFeature("charge", create_does_charge(2), charge_damage("0d6",  STR_STR, 14))
SURE_FOOTED = SavingThrowFeature("sure-footed",  prone_saving, 1, 0)
POUNCE = DamageFeature("pounce", create_does_charge(2), charge_damage("0d6",  STR_STR, 13))
DEATH_BURST = DeathFeature("death burst",death_is_true, death_burst_fun)
UNDEAD_FORTITUDE = DeathFeature("relentless",  fortitude_condition, get_one_hp)
MARTIAL_ADVANTAGE = DamageFeature("matrial advantage", friend_non_incapac, bonus_damage("2d6"))
TWO_HEADED = SavingThrowFeature("two-header", can_use_two_header, 1, 0)
DUERGAR_RESIL = SavingThrowFeature("duergar resilience", can_use_drug, 1, 0)
BRAVE = SavingThrowFeature("brave", is_fright, 1, 0)
GNOME_CUNNING = SavingThrowFeature("gnome cunning", can_use_gnome_cun, 1, 0)
FEY_ANCESTORY = SavingThrowFeature("fey ancestory", is_char, 1, 0)
MAGIC_REISTANCE = SavingThrowFeature("magic resistance", is_magic, 1, 0)
BRUTE = DamageFeature("brute", damage_is_true, added_damage_funct)
LUCKY = ReRollFeature("lucky", re_roll_below(1))
GREAT_WEAPON_FIGHTING = ReRollFeature("great weapon fighting", re_roll_below(2))
SAVAGE_ATTACK = ReRollFeature("savage attack", savage)

feature_list = [SNEAK_ATTACK, DARK_DEVOTION , RELENTLESS_ENDUR, CHARGE, RAMPAGE, PACK_TACTICS, RELENTLESS, 
                TRAMPLING_CHARGE, SURE_FOOTED, POUNCE, DEATH_BURST, UNDEAD_FORTITUDE, MARTIAL_ADVANTAGE , 
                  TWO_HEADED , DUERGAR_RESIL, BRAVE, GNOME_CUNNING, MAGIC_REISTANCE, BRUTE, LUCKY, GREAT_WEAPON_FIGHTING, SAVAGE_ATTACK]

ALL_FEATURES = {} 

for feat in feature_list:
    ALL_FEATURES[feat.name] = feat 