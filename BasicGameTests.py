
from DnDToolkit import *
from Actions import *; 
from Conditions import *; 
from CreatureClasses import *
from Features import friend_in_range; 


modifiers = Modifiers() 
features = FeatureManager([CHARGE])
no_features = FeatureManager()
sword = Attack(4, "2d8", 1, name = "Sword", side_effects= [SideEffect(PRONE, True, DEX_STR, 15)])
arrow = Attack(hit_bonus= 0, damage_type= PIERCING_DAMAGE, attack_type=RANGED, dist= 5, damage_dice_string="1d6", name = "Bow and Arrow")
player1 = Player(ac =5, hp =30, speed = 3, name = "Fuzzy Wuzzy", team = "player", immunities= [SLASHING_DAMAGE], actions=[sword], modifiers=modifiers, features=features)
monster = Creature(ac = 0, hp = 30,speed = 3, name = "Leo", team = "player", actions=[arrow], modifiers=modifiers, features= no_features)
player2 = Creature(12, 30, 3, name = "Bear", team = "monster", actions=[sword], modifiers=modifiers, features= no_features)
map = Grid(5,5, space =3)
#map.place_pieces([monster, monster2])
#null = NullAction()

player_pos = [(4,4), (3,4)]
monster_pos = [(4,0)]

#print(map)
#print("\n\n")


game = Game(players=[player1, player2], monsters = [monster], player_pos=player_pos, monster_pos= monster_pos, map=map)
player1.end_of_turn(game) 
map.move_piece(player1, (4, 1))
arrow.attacker = player1.name 
arrow.target = monster.name
arrow.execute(game, True)
print(monster.features)
print(monster.hp)


#print(player1.features.conditions)


#game.play_game(debug=True) 