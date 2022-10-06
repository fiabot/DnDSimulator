from DnDToolkit import *
import json 

class Action:
    def __init__(self, name):
        self.name = name 
    def __str__(self):
        return self.name 
    def execute(self, game, debug = False):
        """
        implementation of execute varies by action
        """
        pass 

    def avail_actions(self, creature, game):
        """
        return all the possible options 
        for all possible movement of a creature
        return move and action object pairs
        """
        return [(creature.position, self)]
    
    def __str__(self):
        return self.name 

class NullAction(Action):
    """
    doesn't do anything 
    """

    def __init__(self):
        super().__init__("No Action")
    
    def avail_actions(self, creature, game):
        actions = []
        for move in creature.avail_movement(game):
            actions.append((move, self))
        
        return actions 

class Attack(Action):
    def __init__(self, hit_bonus, damage_dice_string, dist, attack_type = MELE, damage_type = SLASHING_DAMAGE, name = "Attack",side_effects =None,  attacker = None, target = None):
        """
        hit bonus = modifer to d20 roll for hit 
        damage_dice_string = damage dice written in the format "2d8" or "2d8 + 4" 
        """
        Action.__init__(self, name) 

        if hit_bonus is None:
            hit_dice_str = "1d20"
        else: 
            hit_dice_str = make_dice_string(1, 20, hit_bonus)
        self.hit_bonus = hit_bonus 
        self.hit_dice = Dice(hit_dice_str)
        self.damage_dice = Dice(damage_dice_string)
        self.target = target 
        self.dist = dist 
        self.attacker = attacker 
        self.attack_type = attack_type 
        self.damage_type = damage_type 
        if side_effects is None:
            side_effects = [] 
        self.side_effects = side_effects 
    
    def execute(self, game, debug = False):
        """
        Excute attack on target
        if target is none, do nothing
        """
        # if there is not a target, dont do anything 
        target = game.get_creature(self.target)
        attacker = game.get_creature(self.attacker)
        if not target is None and not attacker is None: 

            # roll attack applying any special features 
            
            self.hit_dice = Dice(make_dice_string(1, 20, self.hit_bonus))
            hit = attacker.get_hit_dice(self, game, debug).roll() 

            if debug:
                print("{} rolled a {} to hit {} with {}".format(attacker.name, hit, target.name, self.name ))

            # if hit succeeds, deal damage 
            if hit >= target.ac: 
                
                damage = self.damage_dice.roll() + attacker.get_added_damage(self, game, debug)
                target.damage(damage, self.damage_type,game)
                 
                for effect in self.side_effects:
                    effect.execute(target, debug)
                
                if debug: 
                    print("Hit creature {} for {} using {}".format(target.name, damage, self.name))
            
            elif debug: 
                print("Attack {} missed".format(self.name))
        elif debug:
            print("Target or Attacker not found")

    def set_target(self, attacker, target):
        """
        Assign target 
        """
        new_action = deepcopy(self)
        new_action.target = target 
        new_action.attacker = attacker
        new_action.damage_dice = self.damage_dice 
        return new_action 
    
    def avail_targets(self, team, position, grid):
        """
        return a list of enemies within 
        range of attack
        """

        return [enemy for enemy in grid.enemies_in_range(team, position, self.dist) if enemy.hp > 0] 
    
    def avail_actions(self, creature, game):
        actions = [] 

        for move in creature.avail_movement(game):
            

            targets = self.avail_targets(creature.team, move, game.map)

            for target in targets:
                new_action = self.set_target(creature.name, target.name)
                
                actions.append((move, new_action))
        
        return actions 
    
    def __str__(self):
        if self.target != None:
            return "Attack " + str(self.target) + " with " + self.name 
        else: 
            return self.name 

class MultiAttack(Action):
    def __init__(self, attacks):
        self.attacks = attacks 
        attack_names = [attack.name for attack in attacks]
        name = "Multiattack with: " + " and ".join(attack_names)
        super().__init__(name)
    
    def smallest_range_attack(self):
        attack_ranges = [(attack.dist, attack) for attack in self.attacks]
        smallest_range = 10000000
        smallest_attack = None 

        for attack in attack_ranges:
            if attack[0] < smallest_range:
                smallest_range = attack[0]
                smallest_attack = attack[1]
        
        return smallest_attack 
    
    def avail_actions(self, creature, game):
        first_attack_opts = self.smallest_range_attack().avail_actions(creature, game)

        actions = [] 

        for action in first_attack_opts:
            new_attacks = [] 
            for attack in self.attacks:
                new_attacks.append(attack.set_target(creature.name, action[1].target))
            
            actions.append((action[0], MultiAttack(new_attacks)))
        
        return actions 
    
    def execute(self, game, debug=False):
        if (debug):
            print("Attack with multiple attack")
        for attack in self.attacks:
            attack.execute(game, debug)

class TwoHanded(Attack):
    def __init__(self, hit_bonus, damage_dice_string_small, damage_dice_string_large, dist_small, dist_large, attack_type=MELE, damage_type=SLASHING_DAMAGE, name="Attack", side_effects=None, attacker=None, target=None):
        
        super().__init__(hit_bonus, damage_dice_string_small, dist_large, attack_type, damage_type, name, side_effects, attacker, target)

        self.small_damage = Dice(damage_dice_string_small)
        self.large_damage =Dice(damage_dice_string_large)
        self.close_range = dist_small
        self.wide_range = dist_large
    def execute(self, game, debug = False):
        """
        Excute attack on target
        if target is none, do nothing
        """
        # if there is not a target, dont do anything 
        target = game.get_creature(self.target)
        attacker = game.get_creature(self.attacker)
        if not target is None and not attacker is None: 

            # roll attack applying any special features 
            
            self.hit_dice = Dice(make_dice_string(1, 20, self.hit_bonus))
            hit = attacker.get_hit_dice(self, game, debug).roll() 

            if debug:
                print("{} rolled a {} to hit {} with {}".format(attacker.name, hit, target.name, self.name ))

            # if hit succeeds, deal damage 
            if hit >= target.ac: 
                # find if it was one handed or two 
                if game.map.distance(target.position, attacker.position) > self.close_range:
                    if debug:
                        print("Making a one handed attack")
                    damage = self.small_damage.roll() + attacker.get_added_damage(self, game, debug)
                else: 
                    if debug:
                        print("Making a two handed attack")
                    damage = self.large_damage.roll() + attacker.get_added_damage(self, game, debug)
                target.damage(damage, self.damage_type,game)
                 
                for effect in self.side_effects:
                    effect.execute(target, debug)
                
                if debug: 
                    print("Hit creature {} for {} using {}".format(target.name, damage, self.name))
            
            elif debug: 
                print("Attack {} missed".format(self.name))
        elif debug:
            print("Target or Attacker not found")

class SideEffect:
    def __init__(self, inflicted_condition, can_save, save_type= None, save_dc = 0):
        self.inflicted_condition = inflicted_condition
        self.can_save = can_save
        self.save_type = save_type
        self.save_dc = save_dc
    
    def execute(self, target, debug = False):
        # if condition is inflicted 
        if (not self.can_save) or self.save_dc >= target.saving_throw(self.save_type, self.inflicted_condition):
            if debug:
                print("The {} condition was added to creature {} from attack".format(self.inflicted_condition.name, target.name))
            target.add_condition(self.inflicted_condition)