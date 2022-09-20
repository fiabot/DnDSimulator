from os import unlink
import unittest 
from DnDToolkit import * 
from CreatureClasses import * 

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




class TestCreature(unittest.TestCase):

    def test_create(self):
        monster = Creature(ac = 12, hp = 20, speed = 3)
        self.assertEqual(12, monster.ac)
        self.assertEqual(20, monster.hp)
        self.assertEqual(3, monster.speed)
    
    def test_movement(self):
        monster = Creature(ac = 12, hp = 20, speed = 1)
        player= Creature(ac = 12, hp = 20, speed = 3)
        game = Game([player], [monster], [(0,0)], [(3,3)], Grid(5,5))

        self.assertEqual(5, len(monster.avail_movement(game)))
        self.assertGreater(len(player.avail_movement(game)), len(monster.avail_movement(game))) 
    
    def test_actions(self):
        sword = Attack(4, "2d8", 1, name = "Sword", damage_type= SLASHING_DAMAGE, attack_type= MELE) 
        monster = Creature(ac = 12, hp = 20, speed = 1, name = "Monster")
        player= Creature(ac = 12, hp = 20, speed = 3, actions= [sword], name = "Player")
        game = Game([player], [monster], [(0,0)], [(1,1)], Grid(5,5))

        player_acts = player.avail_actions(game)
        monster_acts = monster.avail_actions(game)
        self.assertGreater(len(player_acts), len(monster_acts))

        has_attack = False 
        for act in player_acts: 
            self.assertTrue(isinstance(act[0], (list, tuple)))
            self.assertEqual(2, len(act[0]))
            self.assertTrue(isinstance(act[1], Action))

            if isinstance(act[1], Attack):
                has_attack = True
                self.assertTrue(act[1].name == "Sword")
                self.assertTrue(act[1].target == "Monster")
        
        self.assertTrue(has_attack)




unittest.main()
