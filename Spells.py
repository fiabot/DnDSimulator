import math
from Actions import * 
from Conditions import * 
HEALING_STR = "healing"
ATTACK_SPELL = "attack spell"
SAVE_ATTACK_SPELL = "save attack spell"
AREA_OF_EFFECT_SPELL = "area of effect"
ATTACK_BONUS_SPELL = "attack bonus spell"
TARGET_CREATURE_SPELL = "target creature spell"

class SpellManager():
    def __init__(self, spell_slots, known_spells):
        self.total_spell_slots = spell_slots
        self.current_spell_slots = self.total_spell_slots
        self.known_spells = known_spells
        self.can_concretate = True 
        self.concetrated_spell = None 
    
    def long_rest(self):
        self.current_spell_slots = self.total_spell_slots

    def can_cast(self, spell):
        return self.current_spell_slots >= spell.level 
    
    def cast(self, spell, game):
        self.current_spell_slots -= spell.level 
        if spell.is_conc:
            if not self.can_concretate:
                self.remove_concetration(game)
            self.can_concretate = False 
            self.concetrated_spell = spell 
    
    def remove_concetration(self, game):
        self.concetrated_spell.conc_removed(game)
        self.can_concretate = True 
 

class Spell(Action):
    def __init__(self, level, name, spell_type, is_conc = False, conc_remove = None, caster = None):
        super().__init__(name)
        self.level = level 
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

    def execute(self, game, debug = False):
        caster = game.get_creature(self.caster)

        if not caster is None and not caster.spell_manager is None:
            if debug: 
                print("{} is casting {}".format(self.caster, self.name))
            caster.spell_manager.cast(self, game) 
        elif debug:
            print("problem with {} attempting to cast {}".format(self.caster, self.name))

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
                
                caster.spell_manager.cast(self, game)
                target.heal(self.healing_dice.roll())
    
    def __str__(self):
        return "heal {} with {}".format(self.target, self.name)
            
class AttackSpell(Attack, Spell):
    def __init__(self, level, hit_bonus, damage_dice_string, dist, attack_type=RANGED, damage_type=PIERCING_DAMAGE, name="Attack", side_effects=None, attacker=None, target=None):
        Spell.__init__(self, level, name, spell_type = ATTACK_SPELL, is_conc= False, caster = attacker)
        Attack.__init__(self, hit_bonus, damage_dice_string, dist, attack_type, damage_type, name, side_effects, attacker, target)
    
    def set_target(self, attacker, target):
        """
        Assign target 
        """
        new_action = deepcopy(self)
        new_action.target = target 
        new_action.attacker = attacker
        new_action.caster = attacker
        return new_action 

    def avail_actions(self, creature, game):
        if Spell.can_cast(self, creature, game):
            actions = Attack.avail_actions(self, creature, game)

            for action in actions:
                action[1].caster = action[1].attacker 
            
            return actions
        else:
            return [] 
    
    def execute(self, game, debug=False):
        caster = game.get_creature(self.caster)
        if Spell.can_cast(self, caster, game):
            Spell.execute(self, game, debug) 
            Attack.execute(self, game, debug)

class SaveAttackSpell(AttackSpell):

    def __init__(self, level, save_type, save_dc, damage_dice, dist, half_if_saved = True, side_effect_if_save = False, attack_type=RANGED, damage_type=PIERCING_DAMAGE, name="Attack", side_effects=None, attacker=None, target=None):
        super().__init__(level, -20, damage_dice, dist, attack_type, damage_type, name, side_effects, attacker, target)
        self.type = SAVE_ATTACK_SPELL 
        self.save_type = save_type 
        self.save_dc = save_dc 
        self.save_effects = side_effect_if_save 
        self.half_if_saved = half_if_saved 
    
    def execute(self, game, debug = False):
        """
        Excute attack on target
        if target is none, do nothing
        """
        # if there is not a target, dont do anything 
        target = game.get_creature(self.target)
        attacker = game.get_creature(self.attacker)
        if not target is None and not attacker is None: 
            if self.can_cast(attacker, game):
                Spell.execute(self, game)
                # make saving throw and deal damage 
                    
                damage = self.damage_dice.roll() + attacker.get_added_damage(self, game)

                if target.saving_throw(self.save_type, self.type) < self.save_dc: 
                    target.damage(damage, self.damage_type,game)

                    for effect in self.side_effects:
                        effect.execute(target)
                    
                    if debug: 
                        print("{} hit {} for {}".format(self.name, target.name, damage))

                else:
                    if debug: 
                        print("Creature {} made saving throw for {}".format(self.target, self.name))
                    if (self.half_if_saved):
                        target.damage(math.floor(damage / 2), self.damage_type, game)
                        if debug: 
                            print("{} hit {} for {} halved to {}".format(self.name, target.name, damage, math.floor(damage / 2)))

                    if (self.save_effects):
                        for effect in self.side_effects:
                            effect.execute(target)
                
        elif debug:
            print("Target or Attacker not found")

class AreaSpell(Spell):
    def __init__(self, level, name, save_type, save_dc, damage_dice_str, damage_type, 
                    dist, half_on_save = True, effect_on_save = False, side_effects = None, caster=None):

        super().__init__(level, name, spell_type =AREA_OF_EFFECT_SPELL, is_conc = False, 
                            conc_remove = False, caster =caster)
        
        self.save_type = save_type 
        self.save_dc = save_dc 
        self.damage_dice = Dice(damage_dice_str)
        self.dist = dist 
        self.half_on_save = half_on_save
        self.effect_on_save = effect_on_save 
        
        if side_effects is None:
            self.side_effects = []
        else:
            self.side_effects = side_effects 

        self.damage_type = damage_type 
    
    def set_caster(self, caster):
        spell = deepcopy(self)
        spell.caster = caster.name
        return spell 

    def avail_actions(self, creature, game):

        actions = []
        if Spell.can_cast(self, creature, game):
            for move in creature.avail_movement(game):
                if len(game.map.enemies_in_range(creature.team, move, self.dist)) > 0:
                    actions.append([move, self.set_caster(creature)])
        return actions 


    def execute(self, game, debug = False):
        """
        Apply damage to all creatures 
        within range of caster, 
        excluding caster themself 
        """
        # if there is not a target, dont do anything 
       
        caster = game.get_creature(self.caster)
        if not caster is None: 
             if self.can_cast(caster, game):
                Spell.execute(self, game, debug=debug)
                pieces = game.map.pieces_in_range(caster.position, self.dist, dist_min = 1)
                for piece in pieces: 
                    try: 
                        target = game.get_creature(piece.name)

                        damage = self.damage_dice.roll() + caster.get_added_damage(self, game)

                        if target.saving_throw(self.save_type, self.type) < self.save_dc: 
                            target.damage(damage, self.damage_type,game)

                            for effect in self.side_effects:
                                effect.execute(target)
                            
                            if debug: 
                                print("{} hit {} for {}".format(self.name, target.name, damage))

                        else:
                            if debug: 
                                print("Creature {} made saving throw for {}".format(self.target, self.name))
                            if (self.half_if_saved):
                                target.damage(math.floor(damage / 2), self.damage_type, game)
                                if debug: 
                                    print("{} hit {} for {} halved to {}".format(self.name, target.name, damage, math.floor(damage / 2)))

                            if (self.save_effects):
                                for effect in self.side_effects:
                                    effect.execute(target)
                    except: 
                        pass 

class AttackBonusSpell(Spell):
    def __init__(self, level, name, added_damage_effect, half_if_saved = True, caster=None):
        super().__init__(level, name,  spell_type = ATTACK_BONUS_SPELL, is_conc = False, conc_remove = None, caster = caster)
        self.inflicted_con =Condition(can_act= True, can_move= True, is_alive= True, name = "added damage", 
                                added_damage= added_damage_effect, end_of_turn= REMOVE_AT_END)
    
    def execute(self, game, debug=False):
        caster = game.get_creature(self.caster)

        if not caster is None and not caster.spell_manager is None:
            if debug: 
                print("{} is casting {}".format(self.caster, self.name))
            caster.spell_manager.cast(self) 
            caster.add_condition(self.inflicted_con)
        elif debug:
            print("problem with {} attempting to cast {}".format(self.caster, self.name))

class TargetCreature(Spell):
    def __init__(self, level, name, damage_str, dist, condition_choices = None, caster=None, target = None):
        self.name = name 
        self.damage_dice_str = damage_str
        self.target = target 
        self.dist = dist 
        
        self.condtions = condition_choices 
        self.selected_cond = None 
        super().__init__(level, name, TARGET_CREATURE_SPELL, 
                        is_conc = True, conc_remove = self.remove_concentation_func(), caster = caster)
    
    def remove_concentation_func(self):
        def foo (game):
            caster = game.get_creature(self.caster)
            target = game.get_creature(self.target) 
            if not caster is None:
                caster.features.remove_condition(self.name)
            
            if not self.selected_cond is None and not target is None:
                target.remove_condition(self.selected_cond.name)
        
        return foo 

    def set_target(self, target, caster):
        new_spell = TargetCreature(self.level, self.name, self.damage_dice_str, self.dist, self.condtions, caster.name, target.name)
        return new_spell
 
    def avail_actions(self, creature, game):

        actions = []
        if Spell.can_cast(self, creature, game):
            for move in creature.avail_movement(game):
                for enemy in game.map.enemies_in_range(creature.team, move, self.dist):
                    if self.condtions is None:
                        actions.append([move, self.set_target(enemy, creature)])
                    else:
                        for cond in self.condtions:
                            spell = self.set_target(enemy, creature)
                            spell.selected_cond = cond 
                            actions.append([move, spell])
                        
        return actions 
    
    def execute(self, game, debug=False):
        super().execute(game, debug)
        added_damage =Condition(can_act= True, can_move= True, is_alive= True, name = self.name, 
                                added_damage= target_creature_funct(self.target, self.damage_dice_str), end_of_turn= REMOVE_AT_END)
        caster = game.get_creature(self.caster)
        target = game.get_creature(self.target)
        if not caster is None and not target is None: 
            caster.add_condition(added_damage)
        
        if not self.selected_cond is None and not target is None:
            target.add_condition(self.selected_cond)

