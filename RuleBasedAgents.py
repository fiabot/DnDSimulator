from DnDToolkit import * 
from CreatureClasses import * 
from Spells import * 
from Actions import * 
 
DEFENSE_VALUE_BASE = 100
ATTACK_BONUS_VALUE = 100
SAVING_THROW_MOD_VALUE = 100
HEALTH_MOD = 100

class AggressiveCreature2(Creature):
    """
    choice an action with the 
    highest damage, otherwise 
    get as close as possible to 
    creature """
   
    def __init__(self, ac, hp, speed, modifiers = Modifiers(), features = None, 
                    position = (0,0), name = "Creature", team = "neutral", actions = None, 
                    immunities = None, resistences = None, level = 0.5, spell_manager= None, makes_death_saves = False, 
                    area_weight = 1.5):
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level=level, 
                        spell_manager=spell_manager, makes_death_saves = makes_death_saves)
        self.area_weight = area_weight 
        self.action_order()
    
    def action_order(self):
        self.order_actions = [] 
        for action in self.actions: 
            if isinstance(action, Attack) or isinstance(action, SaveAttackSpell):
                self.order_actions.append((action.damage_dice.expected_value(), action)) 
            elif isinstance(action, AreaSpell):
                self.order_actions.append((action.damage_dice.expected_value() * self.area_weight, action)) 
            else: 
                # doesn't have damage dice 
                self.order_actions.append((-1, action))
        self.order_actions.sort(key = lambda x: x[0], reverse=True)
        self.order_actions = [x[1] for x in self.order_actions] 

    def turn(self, game):
        map = game.map 
        action_index = 0 
        actions = []

        while len(actions) == 0: 
            actions = self.order_actions[action_index].avail_actions(self, game)
            action_index += 1 

        closest_enemy = map.closest_enemy(self.team, self.position) 

        if closest_enemy is None: 
            return actions[0]
        else:
            closest_dist = float("inf")
            closest_action = None
            
            for action in actions: 
                if map.distance(action[0], closest_enemy.position) < closest_dist:
                    closest_dist = map.distance(action[0], closest_enemy.position)
                    closest_action = action 
            
            return closest_action 

class CowardlyCreature(Creature):
    """
    If health is above flee ratio 
        1. move as close to an enemy as possible 
        2. complete action with highest value (damage)
            2.1 for area attacks value is damage multiplied by area weight
    
    if less than flee ratio 
        1. move as far away as possible 
        2. compelete action with highest value
    """
    def __init__(self, ac, hp, speed, modifiers = Modifiers(), features = None, 
                    position = (0,0), name = "Creature", team = "neutral", actions = None, 
                    immunities = None, resistences = None, level = 0.5, spell_manager= None, makes_death_saves = False, 
                    area_weight = 1.5, flee_ratio =0.25):
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level=level, 
                        spell_manager=spell_manager, makes_death_saves = makes_death_saves)
        self.area_weight = area_weight 
        self.flee_ratio = flee_ratio 
        self.times = [] 
    

    def eval_actions(self, action):
        if isinstance(action, MultiAttack):
            damage = 0 
            for i in action.attacks:
                damage += i.damage_dice.expected_value()
            return damage 
        if isinstance(action, Attack) or isinstance(action, SaveAttackSpell):
                return action.damage_dice.expected_value()
        elif isinstance(action, AreaSpell):
            return action.damage_dice.expected_value() * self.area_weight
        else: 
            # doesn't have damage dice 
            return -1 
    def closest_enemy_dist(self, action, game):
        closest_enemy = game.map.closest_enemy(self.team, action[0]) 
        return game.map.distance(closest_enemy.position, action[0])

    def sort_acts_by_dist(self, actions, game, reverse = False):
        actions.sort(key = lambda act: self.closest_enemy_dist(act, game), reverse= reverse)

    def turn(self, game):
        start = time.perf_counter()
        return_act = None 
        map = game.map 
        actions = self.avail_actions(game)

        closest_enemy = map.closest_enemy(self.team, self.position) 
        is_coward = self.hp / self.max_hp < self.flee_ratio 

        dist = float("inf")
        possible_actions = []
        
        for action in actions:
            closest_enemy = map.closest_enemy(self.team, action[0]) 
            if not closest_enemy is None: 
                enemy_dist = map.distance(closest_enemy.position, action[0])
                if not is_coward: 
                    if enemy_dist < dist:
                        possible_actions = [action] 
                        dist = enemy_dist 
                    elif enemy_dist ==  dist: 
                        possible_actions.append(action)
                # find furhtest action that is non-zero 
                elif self.eval_actions(action[1]) != 0: 
                    if enemy_dist < dist:
                        possible_actions = [action] 
                        dist = enemy_dist 
                    elif enemy_dist ==  dist: 
                        possible_actions.append(action)

                
        if len(possible_actions) == 0:
            if is_coward:
                actions.sort(key = lambda x: self.closest_enemy_dist(x, game), reverse = False)
                return_act = actions[0]
            else: 
                actions.sort(key = lambda x: self.closest_enemy_dist(x, game), reverse = True)
                return_act = actions[0]
        else:
            highest_act = float("-inf")
            
            for act in possible_actions:
                eval = self.eval_actions(act[1])
                if  eval > highest_act: 
                    return_act = act 
                    highest_act = eval 
        
        end = time.perf_counter()
        self.times.append(end-start)
        return return_act
    
    def average_time(self):
        if len(self.times) == 0:
            return -1 
        else:
            return sum(self.times) / len(self.times)

class AggressiveCreature(CowardlyCreature):
    def __init__(self, ac, hp, speed, modifiers=Modifiers(), features=None, position=(0, 0), 
                        name="Creature", team="neutral", actions=None, immunities=None, resistences=None, 
                        level=0.5, spell_manager=None, makes_death_saves=False, area_weight=1.5):
        flee_ratio = 0 
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level, spell_manager, makes_death_saves, area_weight, flee_ratio)

class DefensiveCreature(CowardlyCreature):
    def __init__(self, ac, hp, speed, modifiers=Modifiers(), features=None, position=(0, 0), 
                        name="Creature", team="neutral", actions=None, immunities=None, resistences=None, 
                        level=0.5, spell_manager=None, makes_death_saves=False, area_weight=1.5):
        flee_ratio = 1 
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level, spell_manager, makes_death_saves, area_weight, flee_ratio)

class ConversativeCreature(Creature):
    """
    choice an action with the 
    highest damage, otherwise 
    get as close as possible to 
    creature 
    """
    def __init__(self, ac, hp, speed, modifiers = Modifiers(), features = None, 
                    position = (0,0), name = "Creature", team = "neutral", actions = None, 
                    immunities = None, resistences = None, level = 0.5, spell_manager= None, makes_death_saves = False, 
                    area_weight = 1.5, spell_ratio = 0.5):
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level=level, 
                        spell_manager=spell_manager, makes_death_saves = makes_death_saves)
        self.area_weight = area_weight 
        self.spell_ratio = spell_ratio 
        self.times = [] 

    def get_hp_ratio(self, game):
        max_hp = 0 
        cur_hp = 0 
        creatures = game.order 
        for creature in creatures: 
            if creature.team == self.team:
                max_hp += creature.max_hp 
                cur_hp += creature.hp 
        if max_hp == 0:
            print("ZERO ERROR")
            for creature in creatures:
                print("CREATURE: {} with hp {}".format(creature.name, creature.max_hp))
        else:
            return cur_hp / max_hp 

    def eval_actions(self, action):
        if isinstance(action, MultiAttack):
            damage = 0 
            for i in action.attacks:
                damage += i.damage_dice.expected_value()
            return damage 
        elif isinstance(action, Attack) or isinstance(action, SaveAttackSpell):
                return action.damage_dice.expected_value()
        elif isinstance(action, AreaSpell):
            return action.damage_dice.expected_value() * self.area_weight
        elif isinstance(action, TargetCreatureSpell):
            return Dice(action.damage_dice_str).expected_value()
        elif isinstance(action, DefenseSpell):
            return DEFENSE_VALUE_BASE + action.base
        elif isinstance(action, TempHPSpell):
            return Dice(action.temp_dice_str).expected_value() * HEALTH_MOD 
        elif isinstance(action, HealingSpell):
            return action.healing_dice.expected_value() * HEALTH_MOD 
        elif isinstance(action, AttackBonusSpell):
            return ATTACK_BONUS_VALUE 
        elif isinstance(action, SavingThrowModiferSpell): 
            return SAVING_THROW_MOD_VALUE 
        else: 
            # doesn't have damage dice 
            return -1 
    
    def is_spell(self, act): 
        return not (isinstance(act, Spell) and act.level >= 1)

    def turn(self, game):
        start = time.perf_counter()
        map = game.map 
        actions = self.avail_actions(game)

        closest_enemy = map.closest_enemy(self.team, self.position) 
        use_spells = self.get_hp_ratio(game) < self.spell_ratio

        dist = float("inf")
        possible_actions = []
        
        for action in actions:
            closest_enemy = map.closest_enemy(self.team, action[0]) 
            if not closest_enemy is None: 
                enemy_dist = map.distance(closest_enemy.position, action[0])
                if use_spells: 
                    if enemy_dist < dist:
                        possible_actions = [action] 
                        dist = enemy_dist 
                    elif enemy_dist ==  dist: 
                        possible_actions.append(action)

                # don't use spells if above threshold       
                elif not self.is_spell(action[1]):  
                    if enemy_dist < dist:
                        possible_actions = [action] 
                        dist = enemy_dist 
                    elif enemy_dist ==  dist: 
                        possible_actions.append(action) 
        return_act = None
        if len(possible_actions) == 0:
            return_act = actions[0]
        else:
            highest_act = float("-inf")
            return_act = None 
            for act in possible_actions:
                eval = self.eval_actions(act[1])
                if  eval > highest_act: 
                    return_act = act 
                    highest_act = eval 
        end = time.perf_counter()

        self.times.append(end - start)
        return return_act
    
    def average_time(self):
        if len(self.times) == 0:
            return -1 
        else:
            return sum(self.times) / len(self.times)

class ProtectiveCreature(ConversativeCreature):
    def __init__(self, ac, hp, speed, modifiers=Modifiers(), features=None, position=(0, 0), 
                    name="Creature", team="neutral", actions=None, immunities=None, resistences=None,
                     level=0.5, spell_manager=None, makes_death_saves=False, area_weight=1.5):
        spell_ratio = 0.9 
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level, spell_manager, makes_death_saves, area_weight, spell_ratio)
