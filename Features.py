from DnDToolkit import *; 
ATTACK_STR = "attack" 

class FeatureManager: 
    def __init__ (self, features):
        self.features= {} 
        for feat in features: 
            if feat.type in self.features:
                self.features[feat.type].append(feat)
            else: 
                self.features[feat.type] = [feat] 
    
    def get_attack_roll(self, attack, game, creature):
        if ATTACK_STR in self.features:
            for feat in self.features[ATTACK_STR]:
                if feat.condition(game, creature, attack):
                    return feat.dice_from_feature(attack) 
            
            return attack.hit_dice 
        else:
            return attack.hit_dice 
        

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


# conditions 
def friend_in_range(game, attacker, attack):
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


SNEAK_ATTACK = AttackFeature("sneakAttack", friend_in_range, 1, 20)