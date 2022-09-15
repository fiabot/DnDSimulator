from copy import deepcopy 
class Condition:
    def __init__(self, name, can_act, can_move, is_alive, attack_advantage = 0, defense_advantage = 0,
                on_added = None, end_of_turn = None, get_avail_moves = None, does_throw_fail = None, 
                throw_advantage = None):
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
    
    def add_end_of_turn(self, end_funct):
        new_condition = deepcopy(self)
        new_condition.add_end_of_turn = end_funct 
    
    def __str__(self):
        return "{} Condition".format(name)

def create_save_funct(save_type, save_dc):
    def save_throw(condition, creature):
        throw = creature.saving_throw(save_type, condition.name)
        return throw > save_dc 
    return save_throw 

# Set up conditions 
AWAKE = Condition("Awake", can_act = True, can_move = True, is_alive = False)
DEAD = Condition("Dead", can_act = False, can_move = False, is_alive = True)
ASLEEP = Condition("Asleep", can_act = False, can_move = False, is_alive = False)
STABLE = Condition("Stable",  can_act = False, can_move = False, is_alive= False)