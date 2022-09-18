from dataclasses import dataclass
from pyexpat import features
from Conditions import *; 
from DnDToolkit import *; 
from Actions import *; 
from Features import *; 


BASE_SKILLS = {STR_STR : 0, DEX_STR: 0 , CON_STR: 0, INT_STR: 0, WIS_STR : 0, CHAR_STR : 0}

class Modifiers:
    def __init__(self, initiative = 0, skill_dict = BASE_SKILLS, save_dict = BASE_SKILLS):
        self.initative = initiative 
        self.skill_mods = skill_dict 
        self.save_mods = save_dict 

    def initiative_mod(self):
        return self.initative 

    def get_skill_mod (self, type): 
        return self.skill_mods[type] 
    
    def get_save_mod(self, type): 
        return self.save_mods[type]


class Creature:
    def __init__(self, ac, hp, speed, modifiers = Modifiers(), features = None, 
                    position = (0,0), name = "Creature", team = "neutral", actions = [], 
                    immunities = [], resistences = []):
        """
        Initialize a creature 
        ac = numerical armor class 
        hp = max hit points either as value or dice roll, depending on rolled value 
        position = starting position as a tuple of row and column 
        name = name of creature 
        team = what side creatures fights for, decides who is an enemy or friend 
        action = available actions as a list 

        """
        self.ac = ac 
        self.modifiers = modifiers 
        self.max_hp = hp 
        self.hp = self.max_hp # assumes we start with full health  
        self.position = position 
        self.last_pos = position 
        self.name = name 
        self.team = team 
        self.actions = actions 
        self.speed = speed 
        self.null = NullAction() 
        actions.append(self.null) # make sure the null action is included
        self.init_dice = Dice("1d20 + {}".format(self.modifiers.initative))
        
        self.game_data = {} 
        self.resistances = resistences
        self.immunities = immunities 

        if features is None:
            features = FeatureManager() 
        self.features = features 

    def get_hit_dice(self, attack, game):
        """
        return the hit dice after applying any 
        special features 
        """
        return self.features.get_attack_roll(attack, self, game)
    
    def get_added_damage(self, attack, game):
        """
        return additional damage 
        granted from features 
        """
        return self.features.get_added_damage(attack, self, game)

    def damage(self, amount, type, game):
        """
        deal damage to creature 
        """
        if not type in self.immunities:
            if type in self.resistances:
                amount = amount // 2 
            self.hp -= amount
            if self.hp <= 0: 
                self.zero_condition(amount, game) 
    
    def roll_initiative(self):
        """
        Roll( for initative
        by default no modifications 
        """
        return self.init_dice.roll() 
    
    def zero_condition(self, amount, game):
        """
        what happens when creature drops to 
        0 hp

        by default creatures dies, for 
        player they should fall unconcious
        and start making death saves 
        """
        self.hp = 0 # there is not negative HP 
        self.features.drop_to_zero(amount, self, game)
        if self.hp == 0:
            self.die()

    def avail_movement(self, game):
        """
        all available movement depending
        on features 

        by default it will be up to 
        movement speed 
        """
        return self.features.avail_moves(self, game)

    def die(self):
        """
        when creatures is killed 
        """
        self.features.add_condition(DEAD, self)
    
    def avail_actions(self, game):
        """
        total available movmenent and 
        actions combinations 
        """
        if self.can_act():
            total_actions = [] 
            for action in self.actions:
                total_actions += action.avail_actions(self, game) 
            
            return total_actions
        else:
            return self.null.avail_actions(self, game) 
    
    def turn(self, game):
        """
        return a movement and an action

        by default will choose first action
        """
        return self.avail_actions(game)[0]

    def end_of_turn(self, game):
        self.last_pos = self.position 
        self.features.end_of_turn(self, game) 

    def long_rest(self):
        """
        reset stats, as if after 
        a long rest. 

        This can conquer death, unlike the real 
        game. 
        """

        self.hp = self.max_hp
        self.features.reset_conditions() 
        self.game_data = {} 
    
    def skill_check(self, type):
        """
        Roll a skill check 
        using any features 
        """
        return self.features.get_skill_dice(type, self).roll() 
    
    def saving_throw(self, type, effect):
        """
        Roll a skill check using 
        any features 
        """
        return self.features.get_save_dice(type, effect, self).roll() 

    def can_act(self):
        return self.features.can_act() 
    
    def can_move(self):
        return self.features.can_move() 
    
    def is_alive(self):
        return self.features.is_alive() 
    
    def get_defense_advantage(self):
        return self.features.defense_advantage()
    
    def add_condition(self, condition):
        print("Someone added a condition")
        self.features.add_condition(condition, self)
    def has_condition(self, condition):
        return self.features.has_condition(condition) 
    
    def is_stable(self):
        return self.features.is_stable() 
    def __str__(self):
        return self.name

class Player(Creature):
    def zero_condition(self, amount, game): 
        self.hp = 0 # there is not negative HP 
        self.features.drop_to_zero(amount, self, game)
        # make sure that our features didn't change our hp 
        if self.hp == 0 and not (self.has_condition(STABLE) or self.has_condition(ASLEEP) or (not self.is_alive())):
                self.add_condition(ASLEEP)

