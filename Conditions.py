class Condition:
    def __init__(self, can_act, can_move, is_dead, making_death_saves):
        self.can_act = can_act
        self.can_move = can_move 
        self.is_dead = is_dead 
        self.making_death_saves = making_death_saves 


# Set up conditions 
AWAKE = Condition(True, True, False, False)
DEAD = Condition(False, False, True, False)
ASLEEP = Condition(False, False, False, True)
STABLE = Condition(False, False, False, False)