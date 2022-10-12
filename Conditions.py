from copy import deepcopy
import math 
from DnDToolkit import *; 
"""
Define conditions and 
set up constants for base 
conditions 
"""


class Condition:
    """
    A condition is something that 
    can be added to a player throughout 
    the game. This can have a number 
    of effects including: 
        1. effecting advantage of attack or saving throws 
        2. effecting what moves are available to creature 
        3. changing if the creature can move, can act, or is alive 
        4. add extra damage when the affected creatures makes an attack
    
    Additionaly a condition can do something 
        1. when added 
        2. at the end of a creatures turn 
    
    A condition can be removed, either by another 
    source or if an end of turn function returns true 
    
    Conditions are considered immutatable so 
    any changes should be made on a copy 
    """
    def __init__(self, name, can_act, can_move, is_alive, attack_advantage = 0, defense_advantage = 0,
                on_added = None, end_of_turn = None, get_avail_moves = None, does_throw_fail = None, 
                throw_advantage = None, throw_extra = None, does_attack_fail = None, added_damage = None, use_once = False, is_magic = False):
        self.name = name 
        self.can_act = can_act
        self.can_move = can_move 
        self.is_alive = is_alive 
        self.attack_advantage = attack_advantage
        self.defense_advantage = defense_advantage
        self.on_added = on_added 
        self.end_of_turn = end_of_turn 
        self.get_avail_moves = get_avail_moves
        self.does_throw_fail = does_throw_fail 
        self.throw_advantage = throw_advantage 
        self.does_attack_fail = does_attack_fail 
        self.added_damage = added_damage
        self.use_once = use_once
        self.throw_extra = throw_extra
        self.is_magic = False 
    
    def add_end_of_turn(self, end_funct):
        """
        create copy of condition 
        with a end of turn function 
        """
        new_condition = deepcopy(self)
        new_condition.end_of_turn = end_funct 
        return new_condition 

    def add_on_added(self, on_added):
        """
        create a copy of condition 
        with an on added function 
        """
        new_condition = deepcopy(self)
        new_condition.on_added = on_added 
        return new_condition 
    
    def __str__(self):
        return "{} Condition".format(self.name)

# helper functions for conditions 

def create_save_funct(save_type, save_dc, is_magic = False):
    """
    Create an end of turn 
    funciton the removes a 
    condition with a successful
    saving throw 
    """
    def save_throw(condition, creature, game):
        throw = creature.saving_throw(save_type, condition, is_magic)
        return throw > save_dc 
    return save_throw 

def create_save_dis(save_type):
    """
    create a function to give a 
    creature disadvantage to a specific 
    type of saving throw 
    """
    def throw_advantage(type, effect, is_magic):
        if type == save_type: 
            return -1 
        else: 
            return 0
    return throw_advantage 

def half_movement(creature, game):
    """
    an get_available moves function
    where the speed is reduced by half 
    """
    return free_moves(speed = math.ceil(creature.speed / 2), creature = creature, game = game)

def reduce_move_by(reduce_amount):
    """
    an get_avail_moves function 
    that reduced a creatures movement 
    by a constant amount 
    """
    def foo(creature, game):
        return free_moves (speed = creature.speed - reduce_amount, creature = creature, game = game)
    return foo 

def death_save(condition, creature, game):
    """
    An end of turn function 
    to represent a death save 
    """

    roll = Dice("1d20").roll() 
        
    if (roll >= 10):
        
        if (SAVES_STR in creature.game_data):
            creature.game_data[SAVES_STR] += 1 
        else: 
            creature.game_data[SAVES_STR] = 1 
        
        if roll == 20:
            creature.game_data[SAVES_STR] += 1 
        
        if creature.game_data[SAVES_STR] >= 3:
            creature.add_condition(STABLE)
            return True 
        else:
            return False 
    else:
        
        if (FAIL_STR in creature.game_data):
                creature.game_data[FAIL_STR] += 1 
        else: 
            creature.game_data[FAIL_STR] = 1 
        
        
        if roll == 1:
            creature.game_data[FAIL_STR] += 1 
        
        if creature.game_data[FAIL_STR] >= 3:
            creature.add_condition(DEAD)

            return True 
        else:
            return False 

def added_damage_funct(save_type, save_dc, damage_dice_str, halfed_if_save = True):
    """
    create a function to add damage to 
    an attack if the creature fails 
    a saving throw 
    """
    def foo (condtion, attack, creature, game):
        """"
        Have the target make a 
        saving throw using a given 
        dc and saving type 
        """

        target = game.get_creature(attack.target)


        damage = Dice(damage_dice_str).roll() 
        if create_save_funct(save_type, save_dc)(condtion.name, target, game):
            if halfed_if_save:
                return math.floor(damage / 2)
            else: 
                return 0 
        else:
            return damage 
    return foo 

def target_creature_funct(creature_name, damage_dice):
    """
    Add extra damage to a 
    particular creature when that creature 
    is hit 
    """
    def foo (condition, attack, creature, game):
        if attack.target == creature_name:
            return Dice(damage_dice).roll() 
        else:
            return 0
    return foo

def added_saving_throw(dice_str):
    """
    create a function 
    for adding an extra 
    dice roll to a saving 
    throw such as with 
    bless 
    """
    dice = Dice(dice_str)

    def throw_extra(type, effect, is_magic):
        return dice.roll() 
    return throw_extra 

removed_at_end = lambda condition, creature, game :True 
REMOVE_AT_END = lambda condition, creature, game :True 

# Set up base conditions 
AWAKE = Condition("Awake", can_act = True, can_move = True, is_alive = True)

DEAD = Condition("Dead", can_act = False, can_move = False, is_alive = False)

ASLEEP = Condition("Asleep", can_act = False, can_move = False, is_alive = True, end_of_turn= death_save)

STABLE = Condition("Stable",  can_act = False, can_move = False, is_alive= True)

BLINDED = Condition("Blinded", can_act = True, can_move = True, is_alive = True, attack_advantage= -1, defense_advantage= 1)

RESTRAINED = Condition("Restrained", can_act = True, can_move = False, is_alive = True, 
                            attack_advantage= -1, defense_advantage= 1, throw_advantage = create_save_dis(DEX_STR))

INCAPACITATED = Condition("Incapacitated", can_act= False, can_move= True, is_alive = True)

INVISIBLE = Condition("Invisable", can_act= True, can_move= True, is_alive= True, attack_advantage= 1, defense_advantage= -1)

PARALYZED = Condition("Paralyzed", can_act= False, can_move= False, is_alive=True, defense_advantage= 1, 
                             does_attack_fail= lambda type, effect, game : type == DEX_STR or type == STR_STR)

POSIONED = Condition("Poisoned", can_act= True, can_move= True, is_alive=True, throw_advantage = lambda type , effect : -1)


PRONE = Condition("Prone", can_act = True, can_move = True, is_alive = True, 
                    get_avail_moves= half_movement, end_of_turn = removed_at_end)

SPEED_REDUCED_BY_1 = Condition("Speed reduced by 1", can_act = True, can_move = True, is_alive = True, 
                    get_avail_moves= reduce_move_by(1), end_of_turn = removed_at_end)


ATTACK_DISADVANTAGE = Condition("Attack Disadvantage", can_act = True, can_move = True, is_alive = True, attack_advantage= -1)