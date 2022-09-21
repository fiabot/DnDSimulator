from operator import is_
from Actions import * 
HEALING_STR = "healing"
class SpellManager():
    def __init__(self, spell_slots, known_spells):
        self.total_spell_slots = spell_slots
        self.current_spell_slots = self.total_spell_slots
        self.known_spells = known_spells
        self.can_concretate = True 
    
    def long_rest(self):
        self.current_spell_slots = self.total_spell_slots

    def can_cast(self, spell):
        return self.current_spell_slots >= spell.level and (self.can_concretate or not spell.is_conc) 
    
    def cast(self, spell):
        self.current_spell_slots -= spell.level 
        

class Spell(Action):
    def __init__(self, level, name, spell_type, is_conc = False, conc_remove = None, caster = None):
        self.level = level 
        self.name = name 
        self.type = spell_type 
        self.is_conc = is_conc
        self.conc_removed = conc_remove 
        self.caster = caster 
        
    
    def can_cast(self, creature, game):
        if not creature.spell_manager is None: 
            return creature.spell_manager.can_cast(self)
        else: 
            return False 

    def avail_actions(self, creature, game):
        actions = []
        if self.can_cast(creature, game):
            for move in creature.avail_movement(game):
                spell = deepcopy(self)
                spell.caster = creature.name 
                actions.append([move, spell])
            return actions  

        else:
            return []

    def execute(self, game):
        caster = game.get_creature(self.caster)

        if not caster is None and not caster.spell_manager is None:
            caster.spell_manager.case(self) 

class HealingSpell(Spell):
    def __init__(self, level, name,  range, healing_dice_str, caster=None, target = None):
        super().__init__(level, name, spell_type = HEALING_STR, is_conc = False, conc_remove = None, caster = caster)
        self.range = range 
        self.healing_dice = Dice(healing_dice_str)
        self.target = target 
    
    def avail_targets(self, creature, game): 
        targets = [] 
        for move in creature.avail_movement(game):
        
            pieces = game.map.pieces_in_range(move, self.range)

            targets += [(move, piece) for piece in pieces if is_friend(creature, piece) and piece.hp < piece.max_hp]
        return targets 
    
    def can_cast(self, creature, game):
        return super().can_cast(creature, game) and len(self.avail_targets) > 0 
    
    def avail_actions(self, creature, game):
        if super().can_cast(creature, game):
            targets = self.avail_targets(creature, game)
            actions = [] 
            for target in targets:
                new_spell = deepcopy(self)
                new_spell.caster = creature.name 
                new_spell.target = target[1].name 
                actions.append([target[0], new_spell])
            return actions 
        else:
            return [] 
    
    def execute(self, game):
        caster = game.get_creature(self.caster)
        target = game.get_creature(self.target)
        if (not (caster is None or target is None)) and \
            (not caster.spell_manager is None) \
            and super().can_cast(caster, game):
                
                caster.spell_manager.cast(self)
                target.heal(self.healing_dice.roll())
            






