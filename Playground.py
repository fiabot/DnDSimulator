from DnDToolkit import *
from Actions import *; 
from Conditions import *; 
from CreatureClasses import *
from Features import *; 
from BasicAgents import *; 
from JinJerryAgent import *; 
from ShyneAgent import *
from Spells import *; 

# create sample actions 
sword = Attack(4, "2d8", 1, name = "Sword", side_effects= [SideEffect(PRONE, True, DEX_STR, 15)])
arrow = Attack(hit_bonus= 0, 
        damage_type= PIERCING_DAMAGE, attack_type=RANGED, dist= 5, damage_dice_string="1d6", name = "Bow and Arrow")

knock_prone = SideEffect(PRONE, can_save=True, save_type= DEX_STR, save_dc= 15)
trample = Attack(hit_bonus= 2, damage_dice_string= "2d8", dist= 1, 
    damage_type= FORCE_DAMAGE, name = "Trample", side_effects= [knock_prone])

bite = Attack(4, "1d4 + 2", 1, name = "bite", damage_type= SLASHING_DAMAGE)

# create sample spells 
healing_word = HealingSpell(1, "healing word", 2, "1d4")
spell_manager = SpellManager(3, [healing_word])

# sample modifiers 
tank_skills = {STR_STR: 2, CON_STR: 1, DEX_STR: 0, CHAR_STR : 0, INT_STR: -1, WIS_STR: -2}
tank_mod = Modifiers(2, tank_skills, tank_skills) 

rog_skills = {STR_STR: -2, CON_STR: -1, DEX_STR: 2, CHAR_STR : 0, INT_STR: 1, WIS_STR: 0}
rog_mod = Modifiers(-1, rog_skills, rog_skills)

# sample features 
tank_feats = FeatureManager([RELENTLESS_ENDUR])
rog_feats = FeatureManager([SNEAK_ATTACK])

# Human creatures 
tank = HumanCreature(ac = 10, hp = 5, speed = 3, modifiers= tank_mod, 
            features= tank_feats, name = "Barbarian", actions=[sword], resistences=[SLASHING_DAMAGE])

rogue = HumanCreature(ac = 11, hp = 5, speed = 3, modifiers= rog_mod, 
            features= rog_feats, name = "Rogue", actions=[arrow], resistences=[SLASHING_DAMAGE],
            spell_manager= spell_manager)



# agressive creatures 
horse = ShyneCreature(ac = 11, hp = 5, speed= 4, name = "Horse", actions = [trample])
hound = ShyneCreature(ac = 12, hp = 2, speed= 3, name = "Hound", actions = [bite])

# game 
map = Grid(7, 7, space = 3)
game = Game(players = [tank, rogue], monsters = [hound, horse], player_pos=[(0,0), (1, 0)], 
        monster_pos=[(6,6), (5,6)], map = map)


# play game 
result = game.play_game(debug=True)
print("Winner: " , result) 

