from DnDToolkit import *; 
ATTACK_STR = "attack" 
DAMAGE_STR = "damage"
SAVE_STR = "saving"
SKILL_STR = "skill"
DEATH_STR = "death"

class FeatureManager: 
    def __init__ (self, features= [], conditions = []):
        self.features= {} 
        for feat in features: 
            if feat.type in self.features:
                self.features[feat.type].append(feat)
            else: 
                self.features[feat.type] = [feat] 
        
        self.conditions = conditions 
    
    def get_attack_roll(self, attack, creature, game):
        if ATTACK_STR in self.features:
            for feat in self.features[ATTACK_STR]:
                if  feat.condition(attack, creature, game):
                    return feat.dice_from_feature(attack) 
            
            return attack.hit_dice 
        else:
            return attack.hit_dice 
    
    def get_added_damage(self, attack, creature, game): 
        if DAMAGE_STR in self.features:
            for feat in self.features[DAMAGE_STR]:
                if feat.condition(attack, creature, game):
                    return feat.added_damage.roll()  
            
            return 0
        else:
            return 0
    
    def get_save_dice(self, type, effect, creature): 
        mod = creature.modifiers.get_save_mod(type) 
        advantage = 0 
        if SAVE_STR in self.features:
            for feat in self.features[SAVE_STR]:
                if feat.condition(type, effect):
                    mod += feat.modifier_granted 
                    advantage += feat.advantage_granted 
                    
            
        return Dice(make_dice_string(1, 20, mod), advantage) 
    
    def get_skill_dice(self, type, creature): 
        mod = creature.modifiers.get_skill_mod(type) 
        advantage = 0 
        if SKILL_STR in self.features:
            for feat in self.features[SKILL_STR]:
                if feat.condition(type):
                    mod += feat.modifier_granted 
                    advantage += feat.advantage_granted 
                    
            
        return Dice(make_dice_string(1, 20, mod), advantage) 
    
    def drop_to_zero(self, amount, creature, game):
        if DEATH_STR in self.features:
            for feat in self.features[DEATH_STR]: 
                if feat.condition(amount, creature, game):
                    feat.effect(amount, creature, game) 
    
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
        self.conditions.append(condition)
        if not condition.on_added is None: 
            condition.on_added(creature)
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
    def __init__(self, name, condition, added_dice_string):
        super().__init__(DAMAGE_STR, name) 
        self.condition = condition 
        self.added_damage = Dice(added_dice_string) 

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

# effects 
def use_relent(amount, creature, game):
    creature.game_data["Relentless Endurance"] = 1 
    if creature.hp == 0:
        creature.hp = 1 
    
SNEAK_ATTACK = DamageFeature("sneakAttack", friend_in_range, "2d20 + 20")
DARK_DEVOTION = SavingThrowFeature("darkDevotion", charm_fright, 1, 0) 
WISDOM_ADV = SkillCheckFeature("Keen sight", wisd, 1 , 20)
RELENTLESS_ENDUR = DeathFeature("Relentless Endurance", has_relent, use_relent)