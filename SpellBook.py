from Spells import * 
"""
Healing 
    Healing Word
    Cure wounds 
"""
HEALING_WORD = HealingSpell(1, "Healing World", 6, "1d4 + 2") # 2 should be spell casting mod
CURE_WOUNDS = HealingSpell(1, "Cure Wounds",1, "1d8 + 2") # 2 should be spell casting mod 

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
    """

MAGIC_MISSILE = AttackSpell(1, 100, "3d4 + 3", 120, RANGED, FORCE_DAMAGE, name = "Magic Missile") # hits automatically, should cast three seperate missiles 
WITCH_BOLT = AttackSpell(1, None, "1d12", 3, RANGED, LIGHTNING) # 2 should be ranged attack, creature is supposed to be able to deal an additional 1d12 to creature every turn as an action
CHILL_TOUCH = AttackSpell(1, None, "1d8", 12, damage_type= NECROTIC) #2 should be ranged, can't gain temp hit points, undeads gets disadvantage 
THORN_WHIP = AttackSpell(1, None, "1d6", 3, attack_type=MELE, damage_type= PIERCING_DAMAGE) # large or smaller gets pulled closer 
PRODUCE_FLAME = AttackSpell(0 , None, "1d8", 3, attack_type=RANGED, damage_type= FIRE_DAMAGE) # 2 is ranged attack 
SHOCKING_GRASP = AttackSpell(0, None, "1d8", 1, MELE, LIGHTNING) # advantage if wearing metal, can't take reactiosn 
CHROMATIC_ORB = AttackSpell(1, None, "3d8", 9, RANGED, ACID_DAMAGE) # choose what damage: acid, fire, lightining, cold, posiion, thunder 
FIRE_BOLT = AttackSpell(0, None, "1d10", 12, RANGED, FIRE_DAMAGE) # flamable objects also ignited 
RAY_OF_FROST = AttackSpell(0, None, "1d8", 6, RANGED, COLD_DAMAGE, side_effects=[SideEffect(SPEED_REDUCED_BY_1, False)])  

sickness_effect = POSIONED.add_end_of_turn(removed_at_end)
RAY_OF_SICKNESS = AttackSpell(1, 2, "2d8", 6, attack_type= RANGED, 
            damage_type= POISON_DAMAGE, side_effects= [(SideEffect(sickness_effect, True, CON_STR, 12))])

"""
Attack with save 
    Tasha’s Hideous Laughter 
    Vicious Mockery
    Dissonant Whispers 
    Posion spray <-- where the fuck did I find this ??? 
    Acid Splash
"""
laughing = INCAPACITATED.add_end_of_turn(create_save_funct(WIS_STR, 12))# make 12 spell casting dc 
TASHAS_HIDEOUS_LAUGHTER = SaveAttackSpell(1, WIS_STR, 12, "0d4", 3, half_if_saved= False, side_effects=[laughing])
ACID_SPLASH = SaveAttackSpell(0,DEX_STR, 12, "1d6", 6, half_if_saved=False, damage_type = ACID_DAMAGE) # 12 is spell casting dc 

mockery = ATTACK_DISADVANTAGE.add_end_of_turn(removed_at_end) 
VICIOUS_MOCKERY = SaveAttackSpell(0, WIS_STR, 12, "1d4", 6, half_if_saved= False, damage_type= PYSCHIC_DAMAGE, side_effects= mockery)
DISSONANT_WHISPERS = SaveAttackSpell(1, WIS_STR, 12, "3d6", damage_type= PYSCHIC_DAMAGE, half_if_saved= True) # moves closer, deafened automatically saved 

"""
Area of Effect 
    Arms of Hadar <- area of effect damage 
    Burning Hands <- area of effect damage 
    
    Thunderwave < - damage to area and moved 

"""
ARMS_OF_HADAR = AreaSpell(1, "Arms of Hadar", STR_STR, None, "2d6", NECROTIC, 1, half_on_save= True) # can't take reactions 
BURNING_HANDS = AreaSpell(1, "Burning Hands", DEX_STR, None, "3d6", FIRE_DAMAGE, 2, half_on_save= True) # sets other stuff on fire 15 feet 
THUNDERWAVE = AreaSpell(1, "Thunder Wave", CON_STR, None, "2d8", THUNDER, 2, half_on_save= True) #15 feet, creature is pushed away from you 


"""

Attack Bonus 
    Ensaring Strike ← on next hit becomes restrained, takes damage from spikes 
    Hail of Thorns <- extra damage when you hit next if succeeds effect range of people 

    Figure out what to do here 
"""


"""Target Creature 
    Hex <- extra damage whenever you hit target creature 
    Hunter’s mark <- extra damage when you hit """

abilities = [STR_STR, DEX_STR, WIS_STR, INT_STR, CHAR_STR, CON_STR]
hexes = []
for ability in abilities: 
    hexes.append(Condition(ability + "disadvantage", True, True, True, throw_advantage=create_save_dis(ability)))

HEX = TargetCreatureSpell(1, "Hex", "1d6", 9, hexes) 
HUNTERS_MARK = TargetCreatureSpell(1, "Hunter's Mark", "1d6", 9) # advanatage on finding them 


"""Defense 
    Mage Armor <- change the AC of a creature """
MAGE_ARMOR = DefenseSpell(1, "Mage Armor", 1, 13, DEX_STR)

"""Temp HP 
    Armor of Agathys <- temp hp, deals damage to people that hit you
    False Life - temp hp """
ARMOR_OF_AGATHYS = TempHPSpell(1, "Armor of Agathys", "0d4 + 5") # if creature hits you, they take 5 cold damage 
FALSE_LIFE = TempHPSpell(1, "False Life", "1d4 + 4")

"""Saving throw 
    Bless <- concentration, gives bonus on checks until ends, multiple people  
    Resistance ← 1d4 on next saving throw 
    Guidance  <- advantage to one skill check ← changing to saving throw """

BLESS = SavingThrowModiferSpell(1, "Bless", "1d4", 3, one_time= False, attack= True, num_effected= 3)
RESISTANCE = SavingThrowModiferSpell(0, "Resistance", "1d4", 1, one_time= True, attack= False)
# Gudiance is the same as resistance execpt with skill check

"""Obsecure area  
    Faerie Fire  <- gives advantage to attacker inside area, concetration  
    Fog Cloud <- disadvantage to those inside  
    Entangle < – becomes retained 

"""