
import unittest 
import os, sys

parent = os.path.abspath('.')
sys.path.insert(1, parent)
from DnDToolkit import * 
from CreatureClasses import * 
from Spells import * 
    

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
    
    def test_conditions(self):
        monster = Creature(ac = 12, hp = 20, speed = 1, name = "Monster")
        monster.add_condition(RESTRAINED)
        self.assertEqual(1, len(monster.features.conditions))

        # can't add a condition twice 
        monster.add_condition(RESTRAINED)
        self.assertEqual(1, len(monster.features.conditions))

        #remove condition 
        monster.features.remove_condition(RESTRAINED.name)
        self.assertEqual(0, len(monster.features.conditions))
    
    def test_spells(self):
        healing_word = HealingSpell(1, "healing word", 2, "1d4 + 1")
        monster = Creature(ac = 12, hp = 20, speed = 1, spell_manager= SpellManager(3, [healing_word]), name= "monster")
        monster2 = Creature(ac = 12, hp = 20, speed = 1, name = "monster2")
        player= Creature(ac = 12, hp = 20, speed = 3, name = "player")
        game = Game([player], [monster, monster2], [(0,0)], [(4,4), (4,3)], Grid(5,5))
        monster2.hp = 10 
        has_spell = False 
        for action in monster.avail_actions(game):
            if isinstance(action[1], Spell):
                
                has_spell = True 
                self.assertEqual("healing word", action[1].name)
        
        self.assertTrue(has_spell)

        monster.spell_manager.current_spell_slots -= 1 

        monster.long_rest()
        self.assertEqual(3, monster.spell_manager.current_spell_slots)





unittest.main()
