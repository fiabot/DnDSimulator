from distutils.log import debug
import unittest 
import os, sys

parent = os.path.abspath('.')
sys.path.insert(1, parent)
from DnDToolkit import * 
from CreatureClasses import * 
from Spells import * 
    

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


    def test_attack(self):
        witch_bolt = AttackSpell(level = 1, hit_bonus= 3, damage_dice_string= "1d12", 
                dist=3, attack_type=RANGED, damage_type=LIGHTNING, name = "witch bolt")
            
        fire_bolt = AttackSpell(level = 0, hit_bonus= 2, damage_dice_string= "1d10",
                 dist = 12, attack_type= RANGED, damage_type=FIRE_DAMAGE, name = "fire bolt")

        witch = Creature(12, 12, 3, spell_manager= SpellManager(3, [witch_bolt, fire_bolt]), name = "witch")
        monster = Creature(1, 100, 3, name = "monster")

        map = Grid(12, 12)
        game = Game([witch], [monster], [(0, 0)], [(1, 1)],map)

        self.assertEqual(LIGHTNING, witch_bolt.damage_type)
        self.assertEqual(1, witch_bolt.level)
        self.assertTrue(witch_bolt.can_cast(witch, game))

        self.assertGreater(len(witch_bolt.avail_actions(witch, game)), 0)

        for action in witch_bolt.avail_actions(witch, game):
            self.assertEqual(action[1].target, monster.name)
            self.assertEqual(action[1].attacker, witch.name)
            self.assertEqual(action[1].caster, witch.name)
        
        witch_bolt.avail_actions(witch, game)[0][1].execute(game, debug = True)

        self.assertLess(monster.hp, 100)
        print(monster.hp)

        old_hp = monster.hp 

        # move out of the range for witch, but not fire 
        map.move_piece(monster, [4,4])
        self.assertEqual(len(witch_bolt.avail_actions(witch, game)), 0)
        self.assertGreater(len(fire_bolt.avail_actions(witch, game)), 0)

        # us up spell slots 
        map.move_piece(monster, [1,0])
        witch_bolt.avail_actions(witch, game)[0][1].execute(game)
        witch_bolt.avail_actions(witch, game)[0][1].execute(game)
        self.assertEqual(0, witch.spell_manager.current_spell_slots)
        
        # make sure you can't use witch bolt 
        old_hp = monster.hp 
        self.assertEqual(len(witch_bolt.avail_actions(witch, game)), 0)

        witch_bolt.target = monster.name 
        witch_bolt.attacker = witch.name 
        witch_bolt.caster = witch.name
        witch_bolt.execute(game)
        self.assertEqual(old_hp, monster.hp)

        # but fire bolt can 
        old_hp = monster.hp 
        self.assertGreater(len(fire_bolt.avail_actions(witch, game)), 0)

        fire_bolt.avail_actions(witch, game)[0][1].execute(game)
        self.assertLess(monster.hp, old_hp)

    def test_save_attack(self):
        dis_whisp = SaveAttackSpell(1, WIS_STR, save_dc =25, damage_dice= "3d1", dist= 6, half_if_saved=True, 
                    side_effects=[SideEffect(PRONE, False)], name = "Dissonance Whispers" )
        
        spell_caster = Creature(12, 20, 3, spell_manager= SpellManager(3, [dis_whisp]), name = "spell caster")

        monster = Creature(12, 103, 3, name = "monster")
        grid = Grid(5,5)
        game = Game([spell_caster], [monster], [(0,0)], [(1, 1)], map = grid)

        self.assertGreater(len(dis_whisp.avail_actions(spell_caster, game)), 0)

        # should hit for exactly 3, bc save should fail 
        dis_whisp.avail_actions(spell_caster, game)[0][1].execute(game, debug = True)
        self.assertEqual(monster.hp, 100)

        # force monster to make save <-- take 1 damage 
        monster.modifiers.save_mods[WIS_STR] = 25
        dis_whisp.avail_actions(spell_caster, game)[0][1].execute(game, debug = True)
        self.assertEqual(monster.hp, 99)
        
    def test_area_spell(self):
        hadar = AreaSpell(level = 1,name= "Arms of Hadar", save_type= STR_STR, save_dc= 25, 
                            damage_dice_str= "2d6", damage_type= NECROTIC, dist =1)

        caster = Creature(12, 20, 3, spell_manager= SpellManager(3, [hadar]), name = "Caster")
        monster1 = Creature(12, 20, 3, name = "monster 1")
        monster2 = Creature(12, 20, 3, name = "monster2")

        grid = Grid(5,5)
        game = Game([caster], [monster1, monster2], [(3,3)], [(2,3), (4, 3)], map = grid)

        self.assertGreater(len(hadar.avail_actions(caster, game)), 0)
        hadar.avail_actions(caster, game)[0][1].execute(game)
        self.assertLess(monster1.hp, 20)
        self.assertLess(monster2.hp, 20)

       
 
unittest.main()