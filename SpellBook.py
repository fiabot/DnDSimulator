from unittest.mock import NonCallableMagicMock
from Spells import * 
"""
Implements all available spells 

"""


"""
Healing 
    Healing Word
    Cure wounds 
"""
HEALING_WORD = HealingSpell(1, "healing word", 6, "1d4") 
CURE_WOUNDS = HealingSpell(1, "cure wounds",1, "1d8") 

"""
Attack 
    Magic Missile <- three attacks 
    Witch Bolt <- attack, continues to do damage
    Chill touch - damage no temp hp  
    Thorn Whip<- attack, moves creature closer 
    Produce Fire  <- attack with fire 
    Shock Grasp ← attacks 
    Chromoatic Orb 
    Ray of Sickness ← attack with save 
    Fire Bolt 
    Ray of Frost  

    special monster effect:
    Web 
    """

MAGIC_MISSILE = AttackSpell(1, 100, "3d4 + 3", 120, RANGED, FORCE_DAMAGE, name = "magic missile") # hits automatically, should cast three seperate missiles 
WITCH_BOLT = AttackSpell(1, None, "1d12", 3, RANGED, LIGHTNING, name = "witch bolt") # creature is supposed to be able to deal an additional 1d12 to creature every turn as an action
CHILL_TOUCH = AttackSpell(1, None, "1d8", 12, damage_type= NECROTIC, name = "chill touch") #2can't gain temp hit points, undeads gets disadvantage 
THORN_WHIP = AttackSpell(1, None, "1d6", 3, attack_type=MELE, damage_type= PIERCING_DAMAGE, name = "thorn whip") # large or smaller gets pulled closer 
PRODUCE_FLAME = AttackSpell(0 , None, "1d8", 3, attack_type=RANGED, damage_type= FIRE_DAMAGE, name = "produce fire")  
SHOCKING_GRASP = AttackSpell(0, None, "1d8", 1, MELE, LIGHTNING, name = "shocking grasp") # advantage if wearing metal, can't take reactiosn 
CHROMATIC_ORB = AttackSpell(1, None, "3d8", 9, RANGED, ACID_DAMAGE, name = "chromatic orb") # choose what damage: acid, fire, lightining, cold, posiion, thunder 
FIRE_BOLT = AttackSpell(0, None, "1d10", 12, RANGED, FIRE_DAMAGE, name = "fire bolt") # flamable objects also ignited 
RAY_OF_FROST = AttackSpell(0, None, "1d8", 6, RANGED, COLD_DAMAGE, side_effects=[SideEffect(SPEED_REDUCED_BY_1, False)], name = "ray of frost")  

sickness_effect = POSIONED.add_end_of_turn(removed_at_end)
RAY_OF_SICKNESS = AttackSpell(1, 2, "2d8", 6, attack_type= RANGED, 
            damage_type= POISON_DAMAGE, side_effects= [(SideEffect(sickness_effect, True, CON_STR, 12))], name = "ray of sickness")

web_effect = RESTRAINED.add_end_of_turn(create_save_funct(STR_STR, 12, True))
WEB = AttackSpell(0, 5, "0d0", 3, RANGED, PIERCING_DAMAGE, name = "web", side_effects= [SideEffect(web_effect, False)])
"""
Attack with save 
    Tasha’s Hideous Laughter 
    Vicious Mockery
    Dissonant Whispers 
    Posion spray
    Acid Splash
"""
laughing = INCAPACITATED.add_end_of_turn(create_save_funct(WIS_STR, 12))
TASHAS_HIDEOUS_LAUGHTER = SaveAttackSpell(1, WIS_STR, None, "0d4", 3, half_if_saved= False, side_effects=[laughing], name = "tasha's hideous laughter")
ACID_SPLASH = SaveAttackSpell(0, DEX_STR, None, "1d6", 6, half_if_saved=False, damage_type = ACID_DAMAGE, name = "acid splash")  

mockery = ATTACK_DISADVANTAGE.add_end_of_turn(removed_at_end) 
VICIOUS_MOCKERY = SaveAttackSpell(0, WIS_STR, None, "1d4", 6, half_if_saved= False, damage_type= PYSCHIC_DAMAGE, side_effects= mockery, name = "vicious mockery")
DISSONANT_WHISPERS = SaveAttackSpell(1, WIS_STR, None, "3d6",6, damage_type= PYSCHIC_DAMAGE, half_if_saved= True, name = "dissonant whispers") # moves closer, deafened automatically saved 
POISON_SPRAY = SaveAttackSpell(0, CON_STR, None, "1d12", 1, half_if_saved= True, name = "posion spray")


"""
Area of Effect 
    Arms of Hadar <- area of effect damage 
    Burning Hands <- area of effect damage 
    Thunderwave < - damage to area and moved \

    Breath weapons: 
    Steam Breath (Recharge 6) 
    Frost Breath (Recharge 6) 
    Fire Breath (Recharge 6)
    Breath Weapons


"""
ARMS_OF_HADAR = AreaSpell(1, "arms of hadar", STR_STR, None, "2d6", NECROTIC, 1, half_on_save= True) # can't take reactions 
BURNING_HANDS = AreaSpell(1, "burning hands", DEX_STR, None, "3d6", FIRE_DAMAGE, 2, half_on_save= True) # sets other stuff on fire 15 feet 
THUNDERWAVE = AreaSpell(1, "thunder wave", CON_STR, None, "2d8", THUNDER, 2, half_on_save= True) #15 feet, creature is pushed away from you 


STEAM_BREATH = AreaSpell(1, "Steam Breadth", DEX_STR, 10, "1d8", FIRE_DAMAGE, 2, half_on_save= True)
FROST_BREATH = AreaSpell(1, "frost breath", DEX_STR, 10, "2d4", COLD_DAMAGE, 15, half_on_save= True)
FIRE_BREATH = AreaSpell(1, "fire breath", DEX_STR, 11, "2d6", FIRE_DAMAGE, 2, half_on_save=True)
ACID_BREATH = AreaSpell(1, "acid breath", DEX_STR, 11, "4d8", ACID_DAMAGE, 2, half_on_save= True)
BLINDING_BREATH = AreaSpell(1, "blinding breath", DEX_STR, 10, "0d0", FIRE_DAMAGE, 2, 
                                side_effects=[ SideEffect (BLINDED.add_end_of_turn(create_save_funct(DEX_STR, 10, True)), False) ] ) 

slow_effect = PRONE.add_end_of_turn(create_save_funct(DEX_STR, 11, True))
SLOWING_BREATH = AreaSpell(1, "slowing breath", DEX_STR, 11, "0d0",  FIRE_DAMAGE, 2, 
                        side_effects=[SideEffect(slow_effect, False)])

"""

Attack Bonus 
    Ensaring Strike ← on next hit becomes restrained, takes damage from spikes 
    Hail of Thorns <- extra damage when you hit next if succeeds effect range of people 

"""

def ensaring_end_of_turn(save_type, save_dc, damage_dice, damage_type):
    def foo(condition, creature, game):
        print("in end of turn for ensaring")
        if create_save_funct(save_type, save_dc)(condition, creature, game):
            return True 
        else: 
            creature.damage(damage_dice.roll(), damage_type, game)
    return foo 

def ensaring_added_damage_funct(save_type, damage_dice_str, damage_type, name):
    def foo (condtion, attack, creature, game):
        """"
        Have the target make a 
        saving throw using the 
        spell casting dc of the 
        the attacker, if known 
        otherwise dc is 10 

        If save fails, add condition
        that will damage target with 
        1d6 piercing at the end of 
        each turn, along with being 
        restrained. This effect can be 
        saved 
        """

        if creature.spell_manager is None:
            save_dc = 12 
        else: save_dc = creature.spell_manager.spell_dc 

        target = game.get_creature(attack.target)


        if create_save_funct(save_type, save_dc, is_magic=True)(condtion.name, target, game):
                return 0 
        else:
            dice = Dice(damage_dice_str)
            condition = RESTRAINED.add_end_of_turn(ensaring_end_of_turn(save_type, save_dc, dice, damage_type)) 
            condition.name = name
            target.add_condition(condition)
            creature.game_data["target for {}".format(name)] = target.name 
            return 0
    return foo 

# creatures touching cannot save, large creatures don't have advantage, can isn't save when freed  
ENSARING_STRIKE = AttackBonusSpell(1, "ensaring strike", ensaring_added_damage_funct(STR_STR, "1d6", PIERCING_DAMAGE, "ensaring strike"), is_conc=True)


def hail_damage_funct(save_type, damage_dice_str, damage_type):
    def foo (condtion, attack, creature, game):
        """"
        Have the creatures wihtin
        5 feet of targetmake a 
        saving throw using the 
        spell casting dc of the 
        the attacker, if known 
        otherwise dc is 10 

        if fail take damage, 
        or half otherwise 
        """

        if creature.spell_manager is None:
            save_dc = 12 
        else: save_dc = creature.spell_manager.spell_dc 

        target = game.get_creature(attack.target)
        creatures_in_range = game.pieces_in_range(target.position, 1, dist_min = 0)
        dice = Dice(damage_dice_str)

        for creature in creatures_in_range:
            damage = dice.roll() 
            if create_save_funct(save_type, save_dc, is_magic=True)(condtion.name, creature, game):
                    creature.damage(damage//2, damage_type, game)
            else:
                creature.damage(damage, damage_type, game)
        return 0 
    return foo 

HAIL_OF_THRONS = AttackBonusSpell(1, "hail of thorns", hail_damage_funct(DEX_STR, "1d10", PIERCING_DAMAGE))

"""Target Creature 
    Hex <- extra damage whenever you hit target creature 
    Hunter’s mark <- extra damage when you hit """

abilities = [STR_STR, DEX_STR, WIS_STR, INT_STR, CHAR_STR, CON_STR]
hexes = []
for ability in abilities: 
    hexes.append(Condition(ability + "disadvantage", True, True, True, throw_advantage=create_save_dis(ability)))

HEX = TargetCreatureSpell(1, "Hex", "1d6", 9, hexes) 
HUNTERS_MARK = TargetCreatureSpell(1, "hunter's mark", "1d6", 9) # advanatage on finding them 


"""Defense 
    Mage Armor <- change the AC of a creature """
MAGE_ARMOR = DefenseSpell(1, "mage armor", 1, 13, DEX_STR)

"""Temp HP 
    Armor of Agathys <- temp hp, deals damage to people that hit you
    False Life - temp hp """
ARMOR_OF_AGATHYS = TempHPSpell(1, "armor of agathys", "0d4 + 5") # if creature hits you, they take 5 cold damage 
FALSE_LIFE = TempHPSpell(1, "false life", "1d4 + 4")

"""Saving throw 
    Bless <- concentration, gives bonus on checks until ends, multiple people  
    Resistance ← 1d4 on next saving throw 
    Guidance  <- advantage to one skill check ← changing to saving throw """

BLESS = SavingThrowModiferSpell(1, "bless", "1d4", 3, one_time= False, attack= True, num_effected= 3)
RESISTANCE = SavingThrowModiferSpell(0, "resistance", "1d4", 1, one_time= True, attack= False)
# Gudiance is the same as resistance execpt with skill check

"""Obsecure area  
    Faerie Fire  <- gives advantage to attacker inside area, concetration  
    Fog Cloud <- disadvantage to those inside  
    Entangle < – becomes retained 

"""

spell_list = [RESISTANCE, BLESS, FALSE_LIFE, ARMOR_OF_AGATHYS, MAGE_ARMOR, HUNTERS_MARK, 
                        HEX, HAIL_OF_THRONS, ENSARING_STRIKE , THUNDERWAVE , BURNING_HANDS, ARMS_OF_HADAR, 
                        POISON_SPRAY, DISSONANT_WHISPERS,VICIOUS_MOCKERY, ACID_SPLASH, TASHAS_HIDEOUS_LAUGHTER, RAY_OF_SICKNESS,
                         MAGIC_MISSILE, WITCH_BOLT, CHILL_TOUCH, THORN_WHIP , PRODUCE_FLAME, SHOCKING_GRASP, 
                        CHROMATIC_ORB, FIRE_BOLT, RAY_OF_FROST, CURE_WOUNDS, HEALING_WORD, STEAM_BREATH, FROST_BREATH,
                        FIRE_BREATH, ACID_BREATH, BLINDING_BREATH, WEB] 

SPELL_BOOK = {}

for spell in spell_list:
    SPELL_BOOK[spell.name] = spell 