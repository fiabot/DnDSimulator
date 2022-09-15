from ast import Mod
from DnDToolkit import *
from Actions import *; 
from Conditions import *; 
from CreatureClasses import *
from Features import friend_in_range; 


modifiers = Modifiers() 
features = FeatureManager([], conditions= [])
no_features = FeatureManager()
sword = Attack(4, "2d8", 1, name = "Sword")
arrow = Attack(hit_bonus= 0, damage_type= PIERCING_DAMAGE, attack_type=RANGED, dist= 5, damage_dice_string="1d6", name = "Bow and Arrow")
player1 = Player(ac =12, hp =30, speed = 3, name = "Fuzzy Wuzzy", team = "player", immunities= [SLASHING_DAMAGE], actions=[sword], modifiers=modifiers, features=features)
monster = Creature(2, 30, 3, name = "Leo", team = "player", actions=[arrow], modifiers=modifiers, features= no_features)
player2 = Creature(12, 30, 3, name = "Bear", team = "monster", actions=[sword], modifiers=modifiers, features= no_features)
map = Grid(5,5, space =3)
#map.place_pieces([monster, monster2])
#null = NullAction()

player_pos = [(4,4), (3,4)]
monster_pos = [(4,3)]

#print(map)
#print("\n\n")


game = Game(players=[player1, player2], monsters = [monster], player_pos=player_pos, monster_pos= monster_pos, map=map)

print(player1.hp)
sword.set_target(player1.name)
sword.attacker = monster.name
sword.execute(game)
print(player1.hp)

arrow.set_target(player1.name)
arrow.attacker =monster.name
arrow.execute(game)
print(player1.hp)


#game.play_game(debug=True) 