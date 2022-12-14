
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
        self.assertTrue(monster.has_condition(RESTRAINED.name))

        # can't add a condition twice 
        monster.add_condition(RESTRAINED)
        self.assertEqual(1, len(monster.features.conditions))

        #remove condition 
        monster.features.remove_condition(RESTRAINED.name)
        self.assertEqual(0, len(monster.features.conditions))
    
    def test_spells(self):
        healing_word = HealingSpell(1, "healing word", 2, "1d4 + 1")
        monster = Creature(ac = 12, hp = 20, speed = 1, spell_manager= SpellManager(3, mele_modifer= 2,  ranged_modifer= 2, spell_dc= 12, known_spells= [healing_word]), name= "monster")
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
    
    def test_multiattack(self):
        sword = Attack(4, "2d8 + 4", 1, name = "Sword", damage_type= SLASHING_DAMAGE, attack_type= MELE)
        bow = Attack(4, "0d4 + 4", 5, name = "Bow", damage_type= SLASHING_DAMAGE, attack_type= MELE)
        multi_attack = MultiAttack([sword, bow])
        monster = Creature(ac = 1, hp = 20, speed = 1, name = "Monster")
        player= Creature(ac = 12, hp = 20, speed = 3, actions= [multi_attack], name = "Player")
        game = Game([player], [monster], [(0,0)], [(1,1)], Grid(5,5))

        self.assertEquals(sword.name, multi_attack.smallest_range_attack().name)
        self.assertLess(0, len(multi_attack.avail_actions(player, game)))
        self.assertLess(0, len(player.avail_actions(game))) 

        for action in multi_attack.avail_actions(player, game):
            attacks = action[1].attacks 

            for attack in attacks: 
                self.assertEqual(attack.target, monster.name)
                self.assertEqual(attack.attacker, player.name)
        
        multi_attack.avail_actions(player, game)[0][1].execute(game, True)

        self.assertLess(monster.hp, 20)

    def test_two_handed(self):

        sword = TwoHanded(hit_bonus= 4, damage_dice_string_small= "0d3 + 4", damage_dice_string_large= "0d4 + 10", dist_small= 1, dist_large= 5, name = "two handed sword")
        
        monster = Creature(ac = 1, hp = 20, speed = 0, name = "Monster")
        player= Creature(ac = 12, hp = 20, speed = 3, actions= [sword], name = "Player")
        game = Game([player], [monster], [(0,0)], [(1,0)], Grid(10,10))

     
        self.assertLess(0, len(sword.avail_actions(player, game)))
        self.assertLess(0, len(player.avail_actions(game))) 

        for attack in sword.avail_actions(player, game):
            
            self.assertEqual(attack[1].target, monster.name)
            self.assertEqual(attack[1].attacker, player.name)
        
        # large damage (close distance) 
        sword.avail_actions(player, game)[0][1].execute(game, True)

        self.assertEqual(monster.hp, 10)

        # small damage (large distance)
        game.map.move_piece(monster, (3,1))
        sword.avail_actions(player, game)[0][1].execute(game, True)

        self.assertEqual(monster.hp, 6)

        # far away (no actions)
        game.map.move_piece(monster, (9,9))
        self.assertEqual(0, len(sword.avail_actions(player, game)))


    def test_death_saves(self):
        creature = Creature(12, 20, 0, makes_death_saves= True)
        
        game = Game([creature], [], [(0,0)], [(0,0)], map = Grid(5,5))
        creature.damage(100, SLASHING_DAMAGE, game)
        self.assertTrue(creature.has_condition(ASLEEP.name))

        while creature.has_condition(ASLEEP.name):
            if FAIL_STR in creature.game_data: 
                print("FAILS:" , creature.game_data[FAIL_STR])
                self.assertTrue(creature.game_data[FAIL_STR] < 3)
            
            if SAVE_STR in creature.game_data: 
                print("SUCCS:", creature.game_data[SAVE_STR])
                self.assertTrue(creature.game_data[SAVE_STR] < 3)
            self.assertTrue(creature.features.is_alive())
            self.assertFalse(creature.features.can_act())
            self.assertFalse(creature.features.can_move())
            
            creature.end_of_turn(game)
        
        
        
        self.assertTrue((not creature.features.is_alive()) or creature.has_condition(STABLE.name))

            





unittest.main()
