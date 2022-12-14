from dataclasses import dataclass
from pyexpat import features
from Conditions import *; 
from DnDToolkit import *; 
from Actions import *; 
from Features import *; 
"""
Bases classes for 
definine a creature 

"""

BASE_SKILLS = {STR_STR : 0, DEX_STR: 0 , CON_STR: 0, INT_STR: 0, WIS_STR : 0, CHAR_STR : 0}

class Modifiers:
    """
    modifers for making skills checks, 
    saving throws, or inative rolls 
    
    """
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
                    position = (0,0), name = "Creature", team = "neutral", actions = None, 
                    immunities = None, resistences = None, level = 0.5, spell_manager = None, 
                    makes_death_saves = False):
        """
        Initialize a creature 
        ac = numerical armor class 
        hp = max hit points either as value or dice roll, depending on rolled value 
        name = name of creature 
        team = what side creatures fights for, decides who is an enemy or friend 
        action = available actions as a list 
        speed = amount creatures is able to move in grid units 
        features = a feaature manager with any special features added 
        modifers = skill and saving throw mods 
        immunities = damage types the character cannot take damage from
        resistences = damage types the character takes half damage from 
        level = player level or challenge rating 
        spell manager = if the creatures is a spell caster, this will include 
                        spell casting info along with spells known 
        makes death saves = whether the creature dies when at 0 hp, or becomes uncious instead 

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
        self.makes_death_saves = makes_death_saves
        if actions is None:
            self.actions = [] 
        else:
            self.actions = actions 
        self.null = NullAction() 
        self.actions = [act for act in self.actions if not act is None and act.name != "No Action"]
        
        self.actions.append(self.null) # make sure the null action is included
        self.init_dice = Dice(make_dice_string(1, 20, self.modifiers.initiative_mod()))
        
        self.game_data = {} 
        if resistences is None: 
            self.resistances = [] 
        else: 
            self.resistances = resistences
        
        if immunities is None: 
            self.immunities = []
        else:
            self.immunities = immunities
        self.level = level 
        self.spell_manager = spell_manager 
        if not self.spell_manager is None: 
            self.actions += self.spell_manager.known_spells  

        if features is None:
            features = FeatureManager() 
        self.features = features 

        self.op_attack = None 
        for act in self.actions: 
            if (isinstance(act, Attack) and act.attack_type == MELE):
                if self.op_attack is None: 
                    self.op_attack = act 
                else: 
                    if (act.hit_dice.expected_value() > self.op_attack.hit_dice.expected_value()):
                        self.op_attack = act 
        self.has_reaction = True 
        self.damage_taken = 0 

    def change_ac(self, new_ac):
        """
        Temporarily change 
        AC until next long rest 
        """
        self.game_data["base ac"] = self.ac 
        self.ac = new_ac 

    def opportunity_attack(self, creature, game):
        """
        remove an extra melee attack
        on a creautre 
        """
        if not self.op_attack is None and self.has_reaction:
            new_action = self.op_attack.set_target(self.name, creature.name)
            new_action.execute(game) 
            self.has_reaction = False 

    def get_hit(self, attack, game, debug = False):
        """
        return the hit dice after applying any 
        special features 
        """
        return self.features.get_attack_roll(attack, self, game, debug)
    
    def heal(self, amount, debug = False):
        """
        Heal HP up to max hit pints 

        if above 0 and asleep or stable, 
        wake up 
        """
        if self.is_alive():
            self.hp += amount 

            if debug:
                print("Creature {} was healed for {}".format(self.name, amount))

            if self.hp > 0 and self.features.has_condition(ASLEEP.name):
                self.features.remove_condition(ASLEEP.name)
                if debug:
                    print("{} is now awake".format(self.name))

            if self.hp > 0 and self.features.has_condition(STABLE.name):
                self.features.remove_condition(STABLE.name)
                if debug:
                    print("{} is now awake".format(self.name))

            if self.hp > self.max_hp:
                self.hp = self.max_hp 
            
    def get_added_damage(self, attack, game, debug = False):
        """
        return additional damage 
        granted from features 
        """
        return self.features.get_added_damage(attack, self, game, debug)

    def damage(self, amount, type, game):
        """
        deal damage to creature 

        apply immunities and resistences 

        if at or below 0 hp, go to zero condition 
        """
        if self.hp > 0:
            if not type in self.immunities:
                if type in self.resistances:
                    amount = amount // 2 
                self.hp -= amount
                self.damage_taken += amount 

                if not self.spell_manager is None:
                    self.spell_manager.take_damage(amount, self, game)
                if self.hp <= 0: 
                    self.zero_condition(amount, game) 
    
    def roll_initiative(self):
        """
        Roll for intiative 
        using init mod
        """
        return self.init_dice.roll() 
    
    def zero_condition(self, amount, game):
        """
        what happens when creature drops to 
        0 hp

        apply any features that happen
        when a creature drops to 0 

        if still at 0 and creature does 
        not make death saves, creature dies 

        otherwise if still at 0, creature 
        will start making death saves 
        """
        
        self.hp = 0 # there is not negative HP 
        self.features.drop_to_zero(amount, self, game)
        if not self.spell_manager is None: 
            self.spell_manager.remove_concetration(game)
        
        if self.makes_death_saves:
            if self.hp == 0 and not (self.has_condition(STABLE.name) or self.has_condition(ASLEEP.name) or (not self.is_alive())):
                self.uncons_amount  += 1 
                self.add_condition(ASLEEP)
            self.hp = 0 
        elif self.hp == 0:
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
                if action is not None: 
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
        """
        retore reactions and 
        apply any features 
        """
        self.last_pos = self.position 
        self.has_reaction = True 
        self.features.end_of_turn(self, game) 

    def long_rest(self):
        """
        reset stats, as if after 
        a long rest. 

        This can conquer death, unlike the real 
        game. 
        """

        self.hp = self.max_hp
        self.damage_taken = 0 
        self.uncons_amount  = 0
        self.features.reset_conditions() 
        if "base ac" in self.game_data:
            self.ac = self.game_data["base ac"]
        self.game_data = {} 
        self.has_reaction = True 
        if not self.spell_manager is None:
            self.spell_manager.long_rest() 
    
    def skill_check(self, type):
        """
        Roll a skill check 
        using any features 
        """
        return self.features.get_skill_dice(type, self).roll() 
    
    def saving_throw(self, type, effect, is_magic = False):
        """
        Roll a skill check using 
        any features 
        """
        return self.features.get_save_dice(type, effect, self, is_magic = False).roll() 

    def can_act(self):
        return self.features.can_act() 
    
    def can_move(self):
        return self.features.can_move() 
    
    def is_alive(self):
        return self.features.is_alive() 
    
    def get_defense_advantage(self):
        return self.features.defense_advantage()
    
    def add_condition(self, condition, debug = False):
        self.features.add_condition(condition, self, debug)

    def has_condition(self, condition):
        return self.features.has_condition(condition) 
    
    def is_stable(self):
        return self.features.is_stable() 
    
    def __str__(self):
        return self.name


