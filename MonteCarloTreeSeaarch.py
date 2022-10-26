from DnDToolkit import * 
from BasicAgents import *
import time  
from MonsterManual import * 
import math 
from GeneralAgentFunctions import * 

class Node:
    def __init__(self, parent, turn, game):
        self.parent = parent 
        self.children = []; 
        self.game = game 
        self.is_root = parent is None 
        self.is_leaf = True 
        self.is_terminal = game.is_terminal  
        self.value = 0 
        self.sumResults = 0 
        self.visits = 1 
        self.turn = turn

    def expand(self):
        if self.is_leaf: 
            creature = self.game.next_creature()
            actions = creature.avail_actions(self.game)

            for a in actions: 
                # if this is the root node, we want the turn
                # to be the action commit, otherwise we 
                # want it to be the turn of the parent 
                if self.is_root:
                    turn = a 
                else:
                    turn = self.turn 
                new_game = forward_action(a, creature.name, self.game)
                node = Node(self, turn, new_game)
                self.children.append(node) 
            
            self.is_leaf = False 
            
    
    def backprop(self, value): 
        self.visits += 1
        self.sumResults += value 
        self.value = self.sumResults / self.visits 

        if not self.is_root:
            self.parent.backprop(value)
    
    def get_best_child(self):
        highest_value = -100000
        highest_child = None 
        for child in self.children:
            if child.value > highest_value:
                highest_child = child 
                highest_value = child.value 
        
        return highest_child 




class MCTSCreature(Creature):
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
                    immunities = None, resistences = None, debug= True, level = 0.5,
                    spell_manager = None, makes_death_saves = False, simulations = 500, depth = 20, c = 0.50):
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level=level, 
                        spell_manager=spell_manager, makes_death_saves=makes_death_saves)
        self.simlations = simulations 
        self.debug = debug 
        self.times = []  
        self.time_components = {} 
        self.c = c
        self.depth = depth
        

    def decide_action(self, game, creature):
        """
        randomly make an action
        """

        random_action(game, creature)
    


    
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
    def select_node(self, root, num_trials):
        node = root 
        while not node.is_leaf:
            choosen = None 
            choosen_val = - 100000000000000000000000
            for child in node.children:
                select = child.value + self.c * math.sqrt(math.log(num_trials) / child.visits)

                if select > choosen_val:
                    choosen = child
                    choosen_val = select 
            
            node = choosen 
        
        return node 


    def turn(self, game):
        """
        Move forward one action and evaluate state 
        use only the top half of states to expand, 
        conduct random trials 
        """
        start = time.perf_counter()
        root = Node(None, None, game.create_copy())


        for trial in range(self.simlations):
            # selection 
            node = self.select_node(root, trial)

            # expansion 
            node.expand()

            #simulation 
            selected_game = random.choice(node.children).game.create_copy() 
            simulate_game(selected_game, self.depth)
            value = heuristic(self, selected_game)

            #back proprob 
            node.backprop(value)
        end = time.perf_counter()
        self.times.append(end - start)
        return root.get_best_child().turn  
    
    def average_time(self):
        if len(self.times) == 0:
            return -1 
        else:
            return sum(self.times) / len(self.times)
    