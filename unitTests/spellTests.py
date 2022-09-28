
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

    def test_concetration(self):
        spell = Spell(1, "spell", "blank spell", is_conc=True, conc_remove= lambda x : print("con removed"))
        monster = Creature(12, 200, 3, spell_manager= SpellManager(3, [spell]), name = "monster")
        player = Creature(12, 100, 3, spell_manager= SpellManager(3, [spell]), name = "player")

        game = Game([player], [monster], [(0,0)], [(1,2)], Grid(5,5))

        spell.caster = monster.name 
        spell.execute(game)

        self.assertFalse(monster.spell_manager.can_concretate)

        # have the creature take damage and loose concentration 
        monster.damage(100, FIRE_DAMAGE, game)
        self.assertTrue(monster.spell_manager.can_concretate)

        # but if damage is low, it won't loose concentratio n
        monster.modifiers.save_mods[CON_STR] = 40 
        spell.execute(game)
        self.assertFalse(monster.spell_manager.can_concretate)
        monster.damage(20, FIRE_DAMAGE, game)
        self.assertFalse(monster.spell_manager.can_concretate)

        # looses con when dead 
        monster.damage(monster.hp, FIRE_DAMAGE, game)
        self.assertEqual(monster.hp, 0)
        self.assertTrue(monster.spell_manager.can_concretate)


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
        
        witch_bolt.avail_actions(witch, game)[0][1].execute(game)

        self.assertLess(monster.hp, 100)

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
        dis_whisp.avail_actions(spell_caster, game)[0][1].execute(game)
        self.assertEqual(monster.hp, 100)

        # force monster to make save <-- take 1 damage 
        monster.modifiers.save_mods[WIS_STR] = 25
        dis_whisp.avail_actions(spell_caster, game)[0][1].execute(game)
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

    def test_target_spell(self):
        hunter = TargetCreature(1, "hunter's mark", "1d6", 9)
        not_hunter = TargetCreature(1, "not hunter's mark", "1d6", 9)

        witch = Creature(12, 12, 3, spell_manager= SpellManager(3, [hunter]), name = "witch")
        attack = Attack(20, "0d20", 3)
        monster = Creature(1, 100, 3, name = "monster")

        map = Grid(12, 12)
        game = Game([witch], [monster], [(0, 0)], [(1, 1)],map)


        self.assertGreater(len(hunter.avail_actions(witch, game)), 0)
        for spell in hunter.avail_actions(witch, game):
            self.assertEquals(witch.name, spell[1].caster)
            self.assertEquals(monster.name, spell[1].target)
        
        #execute 
        hunter.avail_actions(witch, game)[0][1].execute(game)

        self.assertTrue(witch.has_condition(hunter.name))
        
        # deal extra damage 
        attack.target = monster.name 
        attack.attacker = witch.name 
        attack.execute(game)
        self.assertLess(monster.hp, 100)
        hp1 = monster.hp 

        # uses concentration 
        
        self.assertFalse(witch.spell_manager.can_concretate)
        self.assertIsNotNone(witch.spell_manager.concetrated_spell)
        self.assertEqual(witch.spell_manager.concetrated_spell.name, hunter.name)

        #is removed w/ concentration 
        witch.spell_manager.remove_concetration(game)
        self.assertFalse(witch.has_condition(hunter.name))

        # adding new concentration will remove old 
        hunter.avail_actions(witch, game)[0][1].execute(game)
        self.assertTrue(witch.has_condition(hunter.name))

        not_hunter.avail_actions(witch, game)[0][1].execute(game)
        self.assertTrue(witch.has_condition(not_hunter.name))
        self.assertFalse(witch.has_condition(hunter.name))

    def test_defense_spell(self):
        magic_armor = DefenseSpell(1, "magic armor", 1, 13, DEX_STR)
        monster = Creature(ac = 12, hp = 20, speed = 1, spell_manager= SpellManager(3, [magic_armor]), name= "monster")
        monster2 = Creature(ac = 15, hp = 20, speed = 1, name = "monster2")
        mon3_mods = {DEX_STR: 2, CON_STR: 2, STR_STR: 0, CHAR_STR: -3, INT_STR: -4, WIS_STR: -2}
        monster3 = Creature(ac = 12, hp = 20, speed = 1, modifiers= Modifiers(1, mon3_mods, mon3_mods), name = "monster3")
        player= Creature(ac = 12, hp = 20, speed = 3, name = "player")
        game = Game([player], [monster, monster2, monster3], [(0,0)], [(4,4), (4,3), (3,4)], Grid(5,5))

        # can effect self or mon3
        self.assertLess(0, len(magic_armor.avail_actions(monster, game)))

        for move in magic_armor.avail_actions(monster, game): 
            self.assertTrue(move[1].target == monster.name or move[1].target == monster3.name)
        
        # won't target self if high ac 
        monster.ac = 20
        self.assertLess(0, len(magic_armor.avail_actions(monster, game)))

        for move in magic_armor.avail_actions(monster, game): 
            self.assertTrue(move[1].target == monster3.name)

        # changes ac 
        magic_armor.avail_actions(monster, game)[0][1].execute(game)

        self.assertEquals(15, monster3.ac)

        # changes back after long rest 
        monster3.long_rest()
        self.assertEquals(12, monster3.ac)

    def test_temp_spell(self):
        armor_of_agathy = TempHPSpell(1, "armor of agathsy", "0d4 + 5")
        monster = Creature(ac = 12, hp = 20, speed = 3, spell_manager= SpellManager(3, [armor_of_agathy]), name= "monster")
        monster2 = Creature(ac = 12, hp = 20, speed = 1, name = "monster2")
        player= Creature(ac = 12, hp = 20, speed = 3, name = "player")
        game = Game([player], [monster, monster2], [(0,0)], [(4,4), (4,3)], Grid(5,5))

        self.assertLess(1, len(armor_of_agathy.avail_actions(monster, game)))
        for move in armor_of_agathy.avail_actions(monster, game):
            self.assertEquals(monster.name, move[1].caster)
        armor_of_agathy.avail_actions(monster, game)[0][1].execute(game)

        self.assertEqual(25, monster.hp)

        monster.long_rest()

        self.assertEquals(20, monster.hp)

    def test_save_spell(self):
        bless = SavingThrowModiferSpell(1, "bless", "0d4 + 21", 3, one_time= True, num_effected= 3)
        monster = Creature(ac = 12, hp = 20, speed = 1, spell_manager= SpellManager(3, [bless]), name= "monster")
        monster2 = Creature(ac = 12, hp = 20, speed = 1, name = "monster2")
        monster3 = Creature(ac = 12, hp = 20, speed = 1, name = "monster3")
        monster4 = Creature(ac = 12, hp = 20, speed = 1, name = "monster4")
        monster5 = Creature(ac = 12, hp = 20, speed = 1, name = "monster5")
        monster6 = Creature(ac = 12, hp = 20, speed = 1, name = "monster6")
        player= Creature(ac = 12, hp = 20, speed = 3, name = "player")

        monster_pos = [(5,5), (4,5), (6,5), (5,6), (5,4), (9,9)]
        game = Game([player], [monster, monster2, monster3, monster4, monster5, monster6], [(0,0)], monster_pos, Grid(10,10))

        self.assertEquals(10, len(bless.avail_actions(monster, game)))

        for action in bless.avail_actions(monster, game):
            self.assertTrue(isinstance(action[1], SavingThrowModiferSpell))
            self.assertEqual(monster.name, action[1].caster)
            self.assertIsNotNone(action[1].targets)
            self.assertEqual(3, len(action[1].targets))
            for creature in action[1].targets:
                self.assertTrue(creature.startswith("monster"))
        
        spell0 = bless.avail_actions(monster, game)[0][1]
        spell0.execute(game)

        targets = []
        self.assertEqual(3, len(spell0.targets))

        for target in spell0.targets:
            creature = game.get_creature(target)
            self.assertTrue(creature.has_condition(bless.name))
            targets.append(creature)
        
        # condition works 
        self.assertLess(21, targets[0].saving_throw(DEX_STR, PRONE.name))

        # but only once 
        self.assertGreater(21, targets[0].saving_throw(DEX_STR, PRONE.name))

        # concentation removes it 
        monster.spell_manager.remove_concetration(game)
        self.assertFalse(targets[1].has_condition(bless.name))

        # randomly sampling also works 
        game.map.move_piece(monster6, (3,5))

        self.assertEquals(10, len(bless.avail_actions(monster, game)))

        for action in bless.avail_actions(monster, game):
            self.assertTrue(isinstance(action[1], SavingThrowModiferSpell))
            self.assertEqual(monster.name, action[1].caster)
            self.assertIsNotNone(action[1].targets)
            self.assertEqual(3, len(action[1].targets))
            for creature in action[1].targets:
                self.assertTrue(creature.startswith("monster"))
        
        spell0 = bless.avail_actions(monster, game)[0][1]
        spell0.execute(game)

        targets = []
        self.assertEqual(3, len(spell0.targets))

        for target in spell0.targets:
            creature = game.get_creature(target)
            self.assertTrue(creature.has_condition(bless.name))
            targets.append(creature)

        
    
 
unittest.main()