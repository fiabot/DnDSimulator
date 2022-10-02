import unittest 
import os, sys

parent = os.path.abspath('.')
sys.path.insert(1, parent)
from DnDToolkit import * 
from CreatureClasses import * 
from Spells import * 

class TestGame(unittest.TestCase):
    
    def test_opp_attack(self):

        sword = Attack(4, "2d8", 1, name = "Sword", damage_type= SLASHING_DAMAGE, attack_type= MELE) 
        monster = Creature(ac = 0, hp = 20, speed = 1, name = "Monster")
        player= Creature(ac = 12, hp = 20, speed = 3, actions= [sword], name = "Player")
        game = Game([player], [monster], [(0,0)], [(1,0)], Grid(5,5))

        self.assertEqual(1, game.map.distance(monster.position, player.position))
        game.next_turn(monster, [(4,4), NullAction()])

        self.assertEqual(player.has_reaction, False)
        self.assertLess(monster.hp, 20)

        #make sure they can't use opp twice 
        old_hp = monster.hp 
        game.map.move_piece(monster, (0,0))
        game.next_turn(monster, [(4,4), NullAction()])
        self.assertEqual(old_hp, monster.hp)

        # if creature doesn't have opp attack 
        game.map.move_piece(monster, (0,0))
        game.next_turn(player, [(4,4), NullAction()])
        self.assertEqual(old_hp, monster.hp)

    def test_is_friend(self):
        monster = Creature(ac = 12, hp = 20, speed = 1, team="monster")
        monster2 = Creature(ac = 12, hp = 20, speed = 1, team="monster")
        player= Creature(ac = 12, hp = 20, speed = 3, team = "player")

        self.assertTrue(is_friend(monster, monster2))
        self.assertFalse(is_friend(monster, player))
        self.assertFalse(is_friend(monster, None))
    
    def test_enemies_in_range(self):
        sword = Attack(4, "2d8", 1, name = "Sword", damage_type= SLASHING_DAMAGE, attack_type= MELE) 
        monster = Creature(ac = 0, hp = 20, speed = 1, name = "Monster")
        monster2 = Creature(ac = 0, hp = 20, speed = 1, name = "Monster")
        player= Creature(ac = 12, hp = 20, speed = 3, actions= [sword], name = "Player")
        game = Game([player], [monster, monster2], [(0,0)], [(1,0), (2,2)], Grid(5,5))

        self.assertEqual(1, len(game.map.enemies_in_range(player.team, player.position, 1)))

        for creature in game.map.enemies_in_range(monster.team, monster.position, 1): 
            self.assertEqual(player.name, creature.name)

        self.assertEqual(2, len(game.map.enemies_in_range(player.team, player.position, 5)))

    def test_make_dice_str(self):
        self.assertEquals("1d20 + 4", make_dice_string(1, 20, 4))
        self.assertEquals("2d4 - 3", make_dice_string(2, 4, -3))
        self.assertEquals("5d6", make_dice_string(5, 6))

    def test_dice(self):
        dice = Dice(make_dice_string(1, 20, -40))
        self.assertEquals(-40, dice.modifer)

        dice = Dice("2d6 + 1")
        self.assertEquals(1, dice.modifer)
        self.assertEquals(2, dice.amount)
        self.assertEquals(6, dice.type)

        dice = Dice("4d10+3")
        self.assertEquals(3, dice.modifer)
        self.assertEquals(4, dice.amount)
        self.assertEquals(10, dice.type)

        dice = Dice("1d20")
        self.assertEquals(0, dice.modifer)
        self.assertEquals(1, dice.amount)
        self.assertEquals(20, dice.type)
       
class TestGrid(unittest.TestCase):
    def test_clear(self):
        grid = Grid(5, 5)
        monster = Creature(10, 5, 3, name="Monster")
        grid.place_piece(monster, (0,0))

        self.assertEqual(1, len(grid.pieces))

        grid.clear_grid()

        self.assertEqual(0, len(grid.pieces))

unittest.main()