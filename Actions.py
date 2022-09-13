from DnDToolkit import *
from Features import friend_in_range

class Action:
    def __init__(self, name):
        self.name = name 
    def __str__(self):
        return self.name 
    def execute(self, game):
        """
        implementation of execute varies by action
        """
        pass 

    def avail_actions(self, creature, grid):
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
    
    def avail_actions(self, creature, grid):
        actions = []
        for move in creature.avail_movement(grid):
            actions.append((move, self))
        
        return actions 

class Attack(Action):
    def __init__(self, hit_bonus, damage_dice_string, dist, min_dist = 0, name = "Attack", attacker = None, target = None):
        """
        hit bonus = modifer to d20 roll for hit 
        damage_dice_string = damage dice written in the format "2d8" or "2d8 + 4" 
        """
        Action.__init__(self, name) 

        hit_dice_str = make_dice_string(1, 20, hit_bonus)
        self.hit_bonus = hit_bonus 
        self.hit_dice = Dice(hit_dice_str)
        self.damage_dice = Dice(damage_dice_string)
        self.target = target 
        self.dist = dist 
        self.min_dist = min_dist 
        self.attacker = attacker 
    
    def execute(self, game):
        """
        Excute attack on target
        if target is none, do nothing
        """
        # if there is not a target, dont do anything 
        target = game.get_creature(self.target)
        attacker = game.get_creature(self.attacker)
        if not target is None: 
            # roll attack applying any special features 
            hit = attacker.get_hit_dice(game, self).roll() 

            # if hit succeeds, deal damage 
            if hit >= target.ac: 
                damage = self.damage_dice.roll() + attacker.get_added_damage(game, self)
                target.damage(damage, game)

    def set_target(self, target):
        """
        Assign target 
        """
        self.target = target 
    
    def avail_targets(self, team, position, grid):
        """
        return a list of enemies within 
        range of attack
        """

        return [enemy for enemy in grid.enemies_in_range(team, position, self.dist, dist_min = self.min_dist) if not enemy.condition.is_dead] 
    
    def avail_actions(self, creature, grid):
        actions = [] 

        for move in creature.avail_movement(grid):
            

            targets = self.avail_targets(creature.team, move, grid)

            for target in targets:
                new_action = Attack( self.hit_bonus, str(self.damage_dice), self.dist, self.name, target = target.name, name = self.name, attacker = creature.name)
                actions.append((move, new_action))
        
        return actions 
    
    def __str__(self):
        if self.target != None:
            return "Attack " + str(self.target) + " with " + self.name 
        else: 
            return self.name 
