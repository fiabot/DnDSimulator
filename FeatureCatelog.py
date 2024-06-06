
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

sneak_desc = "When an ally is in range, add an additional 2d6 of damage to your attack"
SNEAK_ATTACK = DamageFeature("sneak attack", friend_in_range, bonus_damage("2d6"), desc= sneak_desc)

dark_desc =" The creature has advantage on saving throws against being charmed or frightened."
DARK_DEVOTION = SavingThrowFeature("dark devotion", charm_fright, 1, 0, desc= dark_desc) 

keen_desc= "The creature has advantage on Wisdom (Perception) checks."
WISDOM_ADV = SkillCheckFeature("keen sight", wisd, 1 , 20)

relent_desc = "When the creature is reduced to 0 HP, you can drop to 1 HP instead once per long rest."
RELENTLESS_ENDUR = DeathFeature("relentless endurance", has_relent, use_relent, desc=relent_desc)

charge_desc = "If the creature moves at least 10ft before an attack, it can roll a DC 13 strength check and deal and additional 2d6 of damage."
CHARGE = DamageFeature("charge", create_does_charge(2), charge_damage("2d6",  STR_STR, 13), desc = charge_desc)


rampage_desc = "When the creature reduces a creature to 0 hit points with a melee attack on its turn, the creature can take a bonus action to move up to half its speed and make a bite attack."
RAMPAGE = DeathFeature("rampage", can_rampage, rampage, desc = rampage_desc) 

pack_desc = "The creature has advantage on an attack roll against a creature if at least one of the creatures's allies is within 5 feet of the creature."
PACK_TACTICS = AttackFeature("pack tactics", friend_in_range, 1, 0, desc = pack_desc)

relent_desc2 = "If the creature takes 7 damage or less that would reduce it to 0 hit points, it is reduced to 1 hit point instead."
RELENTLESS = DeathFeature("relentless", create_damage_less_than(7), get_one_hp, desc = relent_desc2)

#TRAMPLING_CHARGE = DamageFeature("charge", create_does_charge(2), charge_damage("0d6",  STR_STR, 14))
sure_desc = "The creature has advantage on Strength and Dexterity saving throws made against effects that would knock it prone."
SURE_FOOTED = SavingThrowFeature("sure-footed",  prone_saving, 1, 0, desc = sure_desc)

pounce_desc = "If the creature moves at least 20 feet straight toward a creature and then hits it with a attack on the same turn, that target must succeed on a DC 12 Strength saving throw or be knocked prone."
POUNCE = DamageFeature("pounce", create_does_charge(2), charge_damage("0d6",  STR_STR, 13), desc = pounce_desc)

death_desc = "When the creature dies, it explodes. Each creature within 5 feet of the creature must succeed on a DC 10 Dexterity saving throw or take 4 (1d8) fire damage."
DEATH_BURST = DeathFeature("death burst",death_is_true, death_burst_fun, desc = death_desc)

undead_desc = "If damage reduces the creature to 0 hit points, it must make a Constitution saving throw with a DC of 5 + the damage taken, unless the damage is radiant or from a critical hit. On a success, the creature drops to 1 hit point instead."
UNDEAD_FORTITUDE = DeathFeature("undead fortitude",  fortitude_condition, get_one_hp, desc = undead_desc)

martial_desc = "Once per turn, the creature can deal an extra 7 (2d6) damage to a creature it hits with a weapon attack if that creature is within 5 feet of an ally of the creature that isn’t incapacitated."
MARTIAL_ADVANTAGE = DamageFeature("martial advantage", friend_non_incapac, bonus_damage("2d6"), desc = martial_desc)

headed_desc  = " The creature has advantage on Wisdom (Perception) checks and on saving throws against being blinded, charmed, deafened, frightened, stunned, or knocked unconscious."
TWO_HEADED = SavingThrowFeature("two-headed", can_use_two_header, 1, 0, desc= headed_desc)

duegar_resil = "The creature has advantage on saving throws against poison, spells, and illusions, as well as to resist being charmed or paralyzed."
DUERGAR_RESIL = SavingThrowFeature("duergar resilience", can_use_drug, 1, 0, desc= duegar_resil)

brave_desc ="The creature has advantage on saving throws against being frightened."
BRAVE = SavingThrowFeature("brave", is_fright, 1, 0, desc=brave_desc)

cunn_desc = "The creature has advantage on all Intelligence, Wisdom, and Charisma saving throws against magic."
GNOME_CUNNING = SavingThrowFeature("gnome cunning", can_use_gnome_cun, 1, 0, desc = cunn_desc)

fey_desc = "The creature has advantage on Charisma saving throws"
FEY_ANCESTORY = SavingThrowFeature("fey ancestry", is_char, 1, 0, desc = fey_desc)

magic_resist = "The creature has advantage on saving throws against magical attacks or effects"
MAGIC_REISTANCE = SavingThrowFeature("magic resistance", is_magic, 1, 0, desc = magic_resist)


#BRUTE = DamageFeature("brute", damage_is_true, added_damage_funct)
lucky_desc = 'The creature can re-roll and attack roll if they rolled  a 1'
LUCKY = ReRollFeature("lucky", re_roll_below(1), desc = lucky_desc)

weapon_desc = 'The creature can re-roll and attack roll if they rolled 2 or below'
GREAT_WEAPON_FIGHTING = ReRollFeature("great weapon fighting", re_roll_below(2), desc = weapon_desc)
savag_desc = "When the creature scores a critical hit with a melee weapon attack, they can roll one of the weapon's damage dice one additional time and add it to the extra damage of the critical hit"
SAVAGE_ATTACK = ReRollFeature("savage attacks", savage, desc = savag_desc)

feature_list = [SNEAK_ATTACK, DARK_DEVOTION , RELENTLESS_ENDUR, CHARGE, RAMPAGE, PACK_TACTICS, RELENTLESS,  SURE_FOOTED, POUNCE, DEATH_BURST, UNDEAD_FORTITUDE, MARTIAL_ADVANTAGE , 
                  TWO_HEADED , DUERGAR_RESIL, BRAVE, GNOME_CUNNING, MAGIC_REISTANCE, LUCKY, GREAT_WEAPON_FIGHTING, SAVAGE_ATTACK, FEY_ANCESTORY ]

ALL_FEATURES = {} 

for feat in feature_list:
    ALL_FEATURES[feat.name] = feat 