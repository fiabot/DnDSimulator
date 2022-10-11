import unittest 
import os, sys

parent = os.path.abspath('.')
sys.path.insert(1, parent)
from DnDToolkit import * 
from CreatureClasses import * 
from Spells import * 
from Conditions import * 
from Features import * 
from FeatureCatelog import * 

class TestCondition(unittest.TestCase):
    def test_added_damage(self):
        added_damage =Condition(can_act= True, can_move= True, is_alive= True, name = "added damage", 
                                added_damage= added_damage_funct(STR_STR, 25, "1d8", False), end_of_turn= REMOVE_AT_END)
        added_damage2 =Condition(can_act= True, can_move= True, is_alive= True, name = "added damage2", 
                                added_damage= added_damage_funct(STR_STR, 0, "0d8 + 8", True), end_of_turn= REMOVE_AT_END)
        added_damage3 =Condition(can_act= True, can_move= True, is_alive= True, name = "added damage2", 
                                added_damage= added_damage_funct(STR_STR, 0, "1d8", False), end_of_turn= REMOVE_AT_END)
        attack = Attack(20, "0d20", 3)
        
        player = Creature(12, 30, 3, name = "Player", actions = [attack])
        monster = Creature(12, 30, 3, name="Monster")

        grid = Grid(5,5)
        game = Game([player], [monster], [(0,0)], [(1, 1)], grid)

        player.add_condition(added_damage)
        attack.attacker = player.name 
        attack.target = monster.name 
        attack.execute(game, debug=True)

        self.assertGreater(30, monster.hp)
        old_hp = monster.hp

        #removed on next turn 
        player.end_of_turn(game)
        attack.execute(game, debug=True)

        self.assertEquals(old_hp, monster.hp)

        # half damage on save 
        player.add_condition(added_damage2)
        attack.attacker = player.name 
        attack.target = monster.name 
        attack.execute(game, debug=True)

        self.assertEquals(old_hp - 4, monster.hp)
        old_hp2 = monster.hp 

        # no damage on save 
        player.end_of_turn(game)

        player.add_condition(added_damage3)
        attack.attacker = player.name 
        attack.target = monster.name 
        attack.execute(game, debug=True)

        self.assertEquals(old_hp2, monster.hp)

    def test_extra_save(self):
        extra_save = Condition("extra save", can_act= True, can_move= True, is_alive= True, throw_extra= added_saving_throw("0d20 + 21"))
        player = Creature(12, 30, 3, name = "Player")
        monster = Creature(12, 30, 3, name="Monster")

        grid = Grid(5,5)
        game = Game([player], [monster], [(0,0)], [(1, 1)], grid)

        player.add_condition(extra_save)
        self.assertLess(20, player.saving_throw(DEX_STR, PRONE.name))

        # use multiple times 
        self.assertLess(20, player.saving_throw(DEX_STR, PRONE.name))

        # single use condition 
        extra_save_one = Condition("extra save", can_act= True, can_move= True, is_alive= True, 
                    throw_extra= added_saving_throw("0d20 + 21"), use_once= True)
        monster.add_condition(extra_save_one)
        self.assertLess(21, monster.saving_throw(DEX_STR, PRONE.name))
        self.assertGreater(21, monster.saving_throw(DEX_STR, PRONE.name))

    def lucky(self):
        attack = Attack(20, "0d20", 3) 
        hit_dice = Dice("1d20", 4)

        player = Creature(12, 30, 3, name = "Player", actions = [attack])
        monster = Creature(12, 30, 3, name="Monster")

        grid = Grid(5,5)
        game = Game([player], [monster], [(0,0)], [(1, 1)], grid)

        self.assertGreater(LUCKY.new_hit(4, hit_dice, attack, player, game), 4) 

        

        



unittest.main()
