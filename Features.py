from sys import is_finalizing
from Conditions import * 
from DnDToolkit import *; 
ATTACK_STR = "attack" 
DAMAGE_STR = "damage"
SAVE_STR = "saving"
SKILL_STR = "skill"
DEATH_STR = "death"

def clamp_advantage(advantage): 
    if(advantage > 0):
        return 1 
    elif advantage < 0: 
        return -1 
    else: 
        return 0 


class FeatureManager: 
    def __init__ (self, features= [], condition_immunities = []):
        self.feature_list = features 
        self.features= {} 
        for feat in features: 
            if feat.type in self.features:
                self.features[feat.type].append(feat)
            else: 
                self.features[feat.type] = [feat] 
        
        self.conditions = []
        self.condition_immunities = condition_immunities 
    
    def get_attack_roll(self, attack, creature, game):
        if self.does_attack_fail(attack, creature, game):
            return FailDice() 
        else:
            dice = None 
            target_adv = game.get_creature(attack.target).get_defense_advantage()
            con_adv = self.condition_advantage() 
            if ATTACK_STR in self.features:
                i = 0 
                while dice is None and i < len(self.features[ATTACK_STR]):
                    feat = self.features[ATTACK_STR][i]
                    if feat.condition(attack, creature, game):
                        dice = feat.dice_from_feature(attack) 
                    i += 1
                
            # if no features are applied, use default dice 
            if dice is None: 
                dice = attack.hit_dice 

            feature_advantage = dice.default_advantage 
            total_advantage = clamp_advantage(feature_advantage + target_adv + con_adv)


            if isinstance(dice, CompoundDice):
                new_dice_list = []
                for sub_dice in dice.dice_list:
                    if sub_dice.type == 20:
                        new_dice_list.append[Dice(sub_dice.dice_string, total_advantage)]
                    else:
                        new_dice_list.append(sub_dice)
                dice = CompoundDice(new_dice_list)

            elif isinstance(dice, Dice):
                dice = Dice(dice.dice_string, total_advantage)
            return dice 
    
    def get_added_damage(self, attack, creature, game): 
        if DAMAGE_STR in self.features:
            for feat in self.features[DAMAGE_STR]:
                if feat.condition(attack, creature, game):
                    return feat.damage_added(attack, creature, game) 
            
            return 0
        else:
            return 0
    
    def get_save_dice(self, type, effect, creature): 
        if (self.does_throw_fail(type, effect)):
            return FailDice()
        else: 
            mod = creature.modifiers.get_save_mod(type) 
            advantage = 0 
            if SAVE_STR in self.features:
                for feat in self.features[SAVE_STR]:
                    if feat.condition(type, effect):
                        mod += feat.modifier_granted 
                        advantage += feat.advantage_granted 
            
            advantage += self.condition_throw_advantage(type, effect)

                
            return Dice(make_dice_string(1, 20, mod), advantage) 
    
    def get_skill_dice(self, type, creature): 
        if (self.does_throw_fail(type)):
            return FailDice()
        else: 
            mod = creature.modifiers.get_skill_mod(type) 
            advantage = 0 
            if SKILL_STR in self.features:
                for feat in self.features[SKILL_STR]:
                    if feat.condition(type):
                        mod += feat.modifier_granted 
                        advantage += feat.advantage_granted 
            
            advantage += self.condition_throw_advantage(type)
                
            return Dice(make_dice_string(1, 20, mod), advantage) 
    
    def drop_to_zero(self, amount, creature, game):
        if DEATH_STR in self.features:
            for feat in self.features[DEATH_STR]: 
                if feat.condition(amount, creature, game):
                    feat.effect(amount, creature, game) 
    
    def avail_moves(self, creature, game):
        if not self.can_move:
            return [creature.position]
        else:
            moves = None 
            i = 0 
            while moves is None and i < len(self.conditions):
                cond = self.conditions[i]
                if not cond.get_avail_moves is None: 
                    moves = cond.get_avail_moves(creature, game)
                i += 1 

            if moves is None: 
                return free_moves(creature.speed, creature, game)
            else:
                return moves 

    def can_move(self):
        return_bool = True 
        for con in self.conditions:
            return_bool = return_bool and con.can_move 
        
        return return_bool 

    def can_act(self):
        return_bool = True 
        for con in self.conditions:
            return_bool = return_bool and con.can_act
        
        return return_bool 
    
    def is_alive(self):
        return_bool = True 
        for con in self.conditions:
            return_bool = return_bool and con.is_alive
        
        return return_bool 

    def add_condition(self, condition, creature):
        if (not condition.name in self.condition_immunities and 
            not condition.name in [condition.name for condition in self.conditions]):
            self.conditions.append(condition)
            if not condition.on_added is None: 
                condition.on_added(creature)

    def remove_condition(self, condition):
        removed = False 
        i = 0 
        while not removed and i < len(self.conditions):
            if self.conditions[i].name == condition.name:
                self.conditions.remove(self.conditions[i])
            i += 1 
    
    def defense_advantage(self):
        advantage = 0 
        for cond in self.conditions:
            advantage += cond.defense_advantage 
            if(advantage > 1):
                advantage = 1 
            elif advantage < 1: 
                advantage = -1 
        return advantage 

    def condition_advantage(self):
        advantage = 0 
        for cond in self.conditions:
            advantage += cond.attack_advantage 
            if(advantage > 1):
                advantage = 1 
            elif advantage < 1: 
                advantage = -1 
        return advantage 

    def does_throw_fail(self, type, effect = None):
        fail = False 
        i = 0 
        while not fail and i < len(self.conditions):
            cond = self.conditions[i]
            if (not cond.does_throw_fail is None):
                cond.does_throw_fail(type, effect)
            i += 1 
        return fail 
    
    def condition_throw_advantage(self, type, effect = None):
        ad = 0 
        i = 0
        while ad == 0 and i < len(self.conditions):
            cond = self.conditions[i]

            if (not cond.throw_advantage is None):
                ad = cond.throw_advantage(type, effect)

            i += 1 
        return ad 

    def does_attack_fail(self, attack, attacker, game):
        fail = False 
        i = 0
        while not fail and i < len(self.conditions):
            cond = self.conditions[i]
            if not cond.does_attack_fail is None:
                fail = cond.does_attack_fail(attack, attacker, game)
            i += 1 

        return fail 

    def end_of_turn(self, creature, game):
        for cond in self.conditions:
            if not cond.end_of_turn is None:
                if cond.end_of_turn(cond, creature, game):
                    self.remove_condition(cond)
    def is_stable(self):
        return self.has_condition(STABLE)
    
    def has_condition(self, condition):
        has_con = False 
        i = 0 
        while not has_con and i < len(self.conditions):
            has_con = self.conditions[i].name == condition.name
            i += 1 
        return has_con
    def reset_conditions(self):
        self.conditions = [] 
    def __str__(self):
        return_str = ""

        return_str += "\tFeatures: "
        for i in self.feature_list:
            return_str += i.name + " , "

        return_str += "\n\tConditions: "
        for i in self.conditions:
            return_str += i.name + " , "
        return return_str
        
        
class Feature: 
    def __init__(self, type, name):
         self.type = type 
         self.name = name

    def __str__(self):
        return "{} Feature : {}".format(self.type, self.name)

class AttackFeature (Feature):
    def __init__(self, name, condition, advantage, modifer, added_dice = None):
        super().__init__(ATTACK_STR, name)
        self.condition = condition 
        self.advantage = advantage 
        self.modifer = modifer 
        if (not added_dice is None):
            self.has_dice = True 
            self.added_dice = Dice(added_dice)
        else:
            self.has_dice = False 
        

    def dice_from_feature(self, attack): 
        old_dice = attack.hit_dice 
        new_mode = old_dice.modifer + self.modifer 
        new_hit_dice = Dice(make_dice_string(old_dice.amount, old_dice.type, new_mode), self.advantage)

        if(self.has_dice):
            return CompoundDice([new_hit_dice, self.added_dice])
        else: 
            return new_hit_dice 
    
class DamageFeature (Feature): 
    def __init__(self, name, condition, damage_added):
        super().__init__(DAMAGE_STR, name) 
        self.condition = condition 
        self.damage_added = damage_added

class SkillCheckFeature (Feature):
    def __init__(self, name, condition, advantage_granted, modifier_granted):
        super().__init__(SKILL_STR, name)
        self.condition = condition 
        self.advantage_granted = advantage_granted
        self.modifier_granted = modifier_granted 

class SavingThrowFeature(SkillCheckFeature):
    def __init__(self, name, condition, advantage_granted, modifier_granted):
        super().__init__(name, condition, advantage_granted, modifier_granted)
        self.type = SAVE_STR

class DeathFeature(Feature):
    def __init__(self, name, condition, effect):
        super().__init__(DEATH_STR, name)
        self.condition = condition 
        self.effect = effect 

# conditions 
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

wisd = lambda type : type == WIS_STR 
charm_fright = lambda type, effect: effect == "charmed" or effect == "frightened"
has_relent = lambda amount, creature, game: not "Relentless Endurance" in creature.game_data 

def can_rampage(amount, creature, game):
    return game.map.distance(game.map.closest_enemy(creature.team, creature.position).position, creature.position) <= 1


# effects 
def use_relent(amount, creature, game):
    creature.game_data["Relentless Endurance"] = 1 
    if creature.hp == 0:
        creature.hp = 1 

def bonus_damage (dice_string):
    def damage_added (attack,attacker, game):
        return Dice(dice_string).roll() 
    return damage_added 

def does_charge(attack, attacker, game): 
    return game.map.distance(attacker.position, attacker.last_pos) >= 2

def charge_damage(dice_string, save_dc):
    def charge_damage(attack, attacker, game):
        is_prone = attacker.saving_throw(STR_STR, PRONE.name) >= save_dc
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

        
        

    

SNEAK_ATTACK = DamageFeature("Sneak Attack", friend_in_range, bonus_damage("2d20 + 20"))
DARK_DEVOTION = SavingThrowFeature("Dark Devotion", charm_fright, 1, 0) 
WISDOM_ADV = SkillCheckFeature("Keen sight", wisd, 1 , 20)
RELENTLESS_ENDUR = DeathFeature("Relentless Endurance", has_relent, use_relent)
CHARGE = DamageFeature("charge", does_charge, charge_damage("2d6", 13))
RAMPAGE = DeathFeature("Rampage", can_rampage, rampage) 
PACK_TACTICS = AttackFeature("Pack Tactics", friend_in_range, 1, 0)