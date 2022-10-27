from DnDToolkit import * 
from BasicAgents import *
import time  
from MonsterManual import * 
import math 
from GeneralAgentFunctions import * 

class MonteCarloGameSearch(Creature):
    """
    Randomly simulates a bunch of 
    games to a certain depth 
    
    """
    def __init__(self, ac, hp, speed, modifiers = Modifiers(), features = None, 
                    position = (0,0), name = "Creature", team = "neutral", actions = None, 
                    immunities = None, resistences = None, depth = 20, trials = 20,  trimming_raito = 0.25,  debug= True, level = 0.5,
                    spell_manager = None, makes_death_saves = False):
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level=level, 
                        spell_manager=spell_manager, makes_death_saves=makes_death_saves)
        self.depth = depth 
        self.trials = trials 
        self.debug = debug 
        self.times = []  
        self.trimming = trimming_raito 
        self.time_components = {} 

    def decide_action(self, game, creature):
        """
        randomly make an action
        """

        random_action(game, creature)
    
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
        if max_hp == 0:
            print("ZERO ERROR")
            for creature in creatures:
                print("CREATURE: {} with hp {}".format(creature.name, creature.max_hp))
        else:
            return cur_hp / max_hp 

    
    def static_evaluator(self, game):
        """
        return an estimation of how well 
        our team is doing given a 
        grid and an order of creatures s
        """
        return heuristic(self, game)

        
    def simulate_game(self, game, depth):
        """
        simulate a game given depth 
        return the resulting map 

        initiative is the creature going 
        next 

        Assumes that game is a copy 
        """
        return simulate_game(game, depth)
    
    def turn(self, game):
        """
        Move forward one action and evaluate state 
        use only the top half of states to expand, 
        conduct random trials 
        """
        options = self.avail_actions(game) 

        options_evaluations = [[0, option] for option in options] 

        start = time.perf_counter()  
        for i, evaluation in enumerate(options_evaluations): 
            values = [] 
            for trial in range(self.trials): 
                option = evaluation[1] 

                # create a copy of game 
                game_copy = game.create_copy() 

                # do action in game 
                creature = game_copy.update_init() # should return copy of self 
                game_copy.next_turn(creature, option) # complete action  

                # forward simulate 
                game_copy = self.simulate_game(game_copy, self.depth)
                
                # evualute future model 
                new_value = self.static_evaluator(game_copy)

                # new evaluation is average of old and new 
                values.append(new_value)
                
            options_evaluations[i][0] = sum(values) / len(values)
        
        end = time.perf_counter()
        if self.debug:
            self.times.append(end - start) 

        options_evaluations.sort(key = lambda x: x[0], reverse=True)
        return options_evaluations[0][1]
    
    def average_time(self):
        if len(self.times) == 0:
            return -1 
        else:
            return sum(self.times) / len(self.times)
    