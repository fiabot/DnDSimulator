from DnDToolkit import * 
from BasicAgents import *
import time  
from MonsterManual import * 
import math 
from GeneralAgentFunctions import * 

class ShyneCreature(Creature):
    """
    Variation of JinJerry agent that prunes poor preformining solutiosn 

    To make a deciions the following algorithm is implemented:
        1. set options to all my available next moves 
        2. set value for all options to 0 
        3. for depth in depths:
                4. for option in options 
                        5. g = create a copy of the game state 
                        6. preform option in g
                        7. for depth turns randomly preform actions in g
                        8. option_value = (option_value + static evaluator for g) / 2
        10. return action with highest value  
    
    """
    def __init__(self, ac, hp, speed, modifiers = Modifiers(), features = None, 
                    position = (0,0), name = "Creature", team = "neutral", actions = None, 
                    immunities = None, resistences = None, depths = [5, 10, 15,20,25], trimming_raito = 0.25,  debug= True, level = 0.5,
                    spell_manager = None, makes_death_saves = False):
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level=level, 
                        spell_manager=spell_manager, makes_death_saves=makes_death_saves)
        self.depths = depths 
        self.debug = debug 
        self.times = []  
        self.trimming = trimming_raito 
        self.time_components = {} 
        for i in self.depths:
            self.time_components[i] = {"sim": 0, "copy": 0, "total": 0, "inst": 0}

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
        for depth in self.depths:
            for i, evaluation in enumerate(options_evaluations): 
                simulation_start = time.perf_counter() 
                option = evaluation[1] 
                old_value = evaluation[0]

                # create a copy of game 
                game_copy = game.create_copy() 

                copy_end = time.perf_counter() 


                # do action in game 
                creature = game_copy.update_init() # should return copy of self 
                game_copy.next_turn(creature, option) # complete action  

                # forward simulate 
                game_copy = self.simulate_game(game_copy, depth)

                simulate_end = time.perf_counter() 
                
                # evualute future model 
                new_value = self.static_evaluator(game_copy)

                # new evaluation is average of old and new 
                options_evaluations[i][0] = (old_value + 2 * new_value) / 2 

                total_end = time.perf_counter() 

                if self.debug:
                    self.time_components[depth]["copy"] += copy_end - simulation_start 
                    self.time_components[depth]["sim"] += simulate_end - copy_end 
                    self.time_components[depth]["total"] += total_end - simulation_start 
                    self.time_components[depth]["inst"] += 1 
            
            options_evaluations.sort(key = lambda x: x[0], reverse=True) # sort by eval 

            cutoff = math.ceil(len(options_evaluations) * (1 -self.trimming))

            options_evaluations = options_evaluations[:cutoff]
        
        end = time.perf_counter()
        if self.debug:
            self.times.append(end - start) 
     
        return options_evaluations[0][1]
    
    def average_time(self):
        if len(self.times) == 0:
            return -1 
        else:
            return sum(self.times) / len(self.times)
    
    def display_times(self):
        """
        display in depth 
        time anaylsis 
        """
        print("Average total turn time: {}".format(self.average_time()))
        for depth in self.time_components:
            times = self.time_components[depth]
            print("For depth: {}".format(depth))
            print("\tAverage Simulation Time: {}".format(times["total"] / times["inst"]))
            print("\tAverage Copying Time   : {}".format(times["copy"] / times["inst"]))
            print("\tAverage Future Time    : {}".format(times["sim"] / times["inst"]))
            print("Sums: full : {}, copying : {}, future sim: {}".format(times["total"], times["copy"], times["sim"]))

