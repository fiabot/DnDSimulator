from pyexpat import features
from Conditions import *; 
from DnDToolkit import *; 
from Actions import *; 
from Features import *; 

BASE_SKILLS = {STR_STR : 0, DEX_STR: 0 , CON_STR: 0, INT_STR: 0, WIS_STR : 0, CHAR_STR : 0}

class Creature:
    def __init__(self, ac, hp, speed, modifiers, features, position = (0,0), name = "Creature", team = "neutral", actions = []):
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
        self.condition =  AWAKE
        self.position = position 
        self.name = name 
        self.team = team 
        self.actions = actions 
        self.speed = speed 
        self.null = NullAction() 
        actions.append(self.null) # make sure the null action is included
        self.init_dice = Dice("1d20 + {}".format(self.modifiers.initative))
        self.features = features 

    def get_hit_dice(self, game, attack):
        """
        return the hit dice after applying any 
        special features 
        """
        return self.features.get_attack_roll(attack, game, self)
    
    def get_added_damage(self, game, attack):
        """
        return additional damage 
        granted from features 
        """
        return self.features.get_added_damage(attack, game, self)

    def damage(self, amount):
        """
        deal damage to creature 
        """
        self.hp -= amount
        if self.hp <= 0: 
            self.zero_condition() 
    
    def roll_initiative(self):
        """
        Roll( for initative
        by default no modifications 
        """
        return self.init_dice.roll() 
    
    def zero_condition(self):
        """
        what happens when creature drops to 
        0 hp

        by default creatures dies, for 
        player they should fall unconcious
        and start making death saves 
        """
        self.hp = 0 # there is not negative HP 
        self.die()

    def avail_movement(self, grid):
        """
        all available movement within 
        walking speed 
        """

        if self.condition.can_move:
            movement = [self.position] 

            movement += [piece[1] for piece in grid.tiles_in_range(self.position, self.speed) if grid.is_free(piece[1])]
            return movement 
        else:
            return [self.position]

    def die(self):
        """
        when creatures is killed 
        """
        self.condition = DEAD
    
    def avail_actions(self, grid):
        """
        total available movmenent and 
        actions combinations 
        """
        if self.condition.can_act:
            total_actions = [] 
            for action in self.actions:
                total_actions += action.avail_actions(self, grid) 
            
            return total_actions
        else:
            return self.null.avail_actions(self, grid) 
    
    def turn(self, map, game):
        """
        return a movement and an action

        by default will choose first action
        """
        return self.avail_actions(map)[0]
    
    def long_rest(self):
        """
        reset stats, as if after 
        a long rest. 

        This can conquer death, unlike the real 
        game. 
        """

        self.hp = self.max_hp
        self.condition = AWAKE 
    
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

    def __str__(self):
        return self.name


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