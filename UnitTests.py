
import unittest 
from DnDToolkit import * 
from CreatureClasses import * 
from Spells import * 
"""
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

class TestSpells(unittest.TestCase):

    def test_healing(self):
        healing_word = HealingSpell(1, "healing word", 2, "1d4 + 1")
        monster = Creature(ac = 12, hp = 20, speed = 1, spell_manager= SpellManager(3, [healing_word]), name= "monster")
        monster2 = Creature(ac = 12, hp = 20, speed = 1, name = "monster2")
        player= Creature(ac = 12, hp = 20, speed = 3, name = "player")
        game = Game([player], [monster, monster2], [(0,0)], [(4,4), (4,3)], Grid(5,5))

        # can't heal past max 
        self.assertEqual(0, len(healing_word.avail_actions(monster, game)))

        healing_word.target = monster2.name 
        healing_word.caster = monster.name 
        healing_word.execute(game)  #<- slot 1 
        self.assertEqual(20, monster2.hp)

        # Will heal at least 2
        monster2.hp = 10 
        self.assertNotEqual(0, len(healing_word.avail_actions(monster, game)))

        spell_inst = healing_word.avail_actions(monster, game)[0][1]
        self.assertEqual(spell_inst.name, "healing word")
        spell_inst.execute(game) # <slot 2

        self.assertGreater(monster2.hp, 11)

        # can't heal if not in range 
        game.map.move_piece(monster2, (1,0))
        self.assertEqual(0, len(healing_word.avail_actions(monster, game)))

        # can't use too many spell slots 
        game.map.move_piece(monster2, (4,3))
        monster2.hp = 1 

        healing_word.target = monster2.name 
        healing_word.caster = monster.name 
        healing_word.execute(game) #<- slot 3

        new_hp = monster2.hp 
        self.assertEquals(0, monster.spell_manager.current_spell_slots)
   
        self.assertEqual(0, len(healing_word.avail_actions(monster, game))) 

        healing_word.target = monster2.name 
        healing_word.caster = monster.name 
        healing_word.execute(game) #<- slot empty 

        self.assertEqual(new_hp, monster2.hp)

"""

class TestCreature(unittest.TestCase):

    """def test_create(self):
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
        monster.features.remove_condition(RESTRAINED)
        self.assertEqual(0, len(monster.features.conditions))"""
    
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
