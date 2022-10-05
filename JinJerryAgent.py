from DnDToolkit import * 
from BasicAgents import *
import time  
#from MonsterManual import * 

class JinJerryCreature(Creature):
        
    def __init__(self, ac, hp, speed, modifiers = Modifiers(), features = None, 
                    position = (0,0), name = "Creature", team = "neutral", actions = None, 
                    immunities = None, resistences = None, makes_death_saves = False, depth = 40, debug= False, level = 0.5, 
                    spell_manager = None):
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level=level, 
                        spell_manager=spell_manager, makes_death_saves=makes_death_saves)
        self.depth = depth 
        self.debug = debug 
        self.times = [] 
    
    def forward_model(self, map, creature, turn):
        """
        simulates a next turn given a turn 
        a creature to preform that turn

        assumes that map is a copy 
        and not the main game map
        """

        #TODO figure out way to abstact this 

        #move creature 
        map.move_piece(creature, turn[0])

        # complete actions 
        turn[1].execute()

        return map 

    def decide_action(self, game, creature):
        """
        choices how the model 
        decides on an action

        by default is random 
        """

        avail_moves = [] 
        while len(avail_moves) == 0:
            action = random.choice(creature.actions) 
            avail_moves = action.avail_actions(creature, game)
        #avail_moves = creature.avail_actions(grid)

        return random.choice(avail_moves)
    
    def get_hp_ratio(self, creatures, team, equal = True):
        """
        returns a teams hp as a 
        ratio of their max hp
        """
        max_hp = 0 
        cur_hp = 0 
        for creature in creatures: 
            if (creature.team == team and equal) or (creature.team != team and (not equal)):
                max_hp += creature.max_hp 
                cur_hp += creature.hp 
        return cur_hp / max_hp 

    
    def static_evaluator(self, game):
        """
        return an estimation of how well 
        our team is doing given a 
        grid and an order
        """
        order = game.order 
        return self.get_hp_ratio(order, self.team) - self.get_hp_ratio(order, self.team, equal=False)

        
    def simulate_game(self, game):
        """
        simulate a game given depth of 4 
        return the resulting map 

        initiative is the creature going 
        next 

        Assumes that game is a copy 
        """
        depth = 0 

        while depth < self.depth:
            creature = game.update_init() 
            turn = self.decide_action(game, creature)
            game.next_turn(creature, turn)
            
            depth += 1 
        return game
    
    def turn(self, game):
        map = game.map
        options = self.avail_actions(game) 

        options_evaluations = [] 

        total_start = time.perf_counter()  
        for option in options: 

            # create a copy of game 
            game_copy = game.create_copy() 

            # do action in game 
            creature = game_copy.update_init() # should return copy of self 
            game_copy.next_turn(creature, option) # complete action  

            # evaluate option 
            action_value = self.static_evaluator(game_copy)


            # forward simulate 
            game_copy = self.simulate_game(game_copy)
            
            
            # evualute future model 
            next_value = self.static_evaluator(game_copy)


            # this turns value is the max of first eval and future eval 
            options_evaluations.append((max(action_value, next_value), option))
                

        
        options_evaluations.sort(key = lambda x: x[0], reverse=True) # sort by eval 

        total_end = time.perf_counter()
        self.times.append(total_end - total_start)
        if self.debug:
            print(f"Time: {total_end - total_start:0.4f}")
        
     
        return options_evaluations[0][1]
    
    def average_time(self):
        return sum(self.times) / len(self.times) 




   






