from DnDToolkit import * 
from BasicAgents import *
import time  
from MonsterManual import * 
import math 
from GeneralAgentFunctions import * 

class Node:
    def __init__(self, parent, turn):
        self.parent = parent 
        self.children = []; 
        self.game = None
        self.is_root = parent is None 
        self.depth = 0 
        self.value = 0 
        self.weighted_value = 0 
        self.sumResults = 0 
        self.visits = 1
        self.terminal_visits = 0 
        self.turn = turn
        self.actions = [] 
        self.creature = None 
        self.is_leaf = True 
        self.is_terminal = False 
        

    def initalize_children(self):
        
        if self.is_leaf and not self.game is None: 
            if not self.is_root:
                self.creature = self.game.next_creature()
            actions = self.creature.avail_actions(self.game)
            for action in actions:
                n = Node(self, action)
                n.depth = self.depth + 1 
                self.children.append(n)
            self.is_leaf = False 


    def has_unexplored_children(self):
        
        has_unex = False 
        i = 0 
        if len(self.children) == 0:
            self.initalize_children()

        while not has_unex and i < len(self.children):
            if self.children[i].game is None: 
                has_unex = True
            i += 1 
        
        return has_unex 
    
    def get_unexplored(self):
        unexplored = [] 

        if len(self.children) == 0:
            self.initalize_children()

        for child in self.children: 
            if child.game is None:
                unexplored.append(child)
        
        return unexplored 
    
    def get_rand_unexplored_action(self):
        unexplored = self.get_unexplored()
        return random.choice(unexplored)

    def get_state(self, child):
        if not child.is_root:
            creature = child.parent.creature
            action = child.turn
            new_state = forward_action(action, creature.name, self.game)
            
            return new_state 
        else:
            return child.game 
        
    def add_state_child(self, child, root_creature):
        child.game = self.get_state(child)
        child.is_terminal = child.game.is_terminal()
        child.initalize_children()
        
        return child
    
    def explore_rand_child(self, root_creature):
        child = self.get_rand_unexplored_action()
        return self.add_state_child(child, root_creature)
    
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
            if child.sumResults > highest_value:
                highest_child = child 
                highest_value = child.value 
        
        return highest_child 




class OLETSCreature(Creature):
    """
    OLETS algorithm from 
    general game playing competition 
    
    """
    def __init__(self, ac, hp, speed, modifiers = Modifiers(), features = None, 
                    position = (0,0), name = "Creature", team = "neutral", actions = None, 
                    immunities = None, resistences = None, debug= True, level = 0.5,
                    spell_manager = None, makes_death_saves = False, simulations = 1500, depth = 20, c = 0.50):
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
    
    def OLE(self, parent, child):
        score = child.sumResults + math.sqrt(math.log(parent.visits) / child.visits)
        return score 
    
    def max_OLE(self, parent): 
        highest = float("-inf") 
        node = None 
        for i in parent.children:
            ole = self.OLE(parent, i)
            if ole > highest:
                highest = ole 
                node = i 
        
        return node 
    
    def sum_results(self, node):
        if len(node.children) == 0:
            print(node.visits)
        max_child = max([c.sumResults for c in node.children]) 
        return (node.value / node.visits) + ((1 - node.terminal_visits) / node.visits) * max_child
    
    def run_simulation(self, root: Node):
        node = root 
        exit = False 

        # get new node 
        while not exit and not node.is_terminal:
            
            if node.has_unexplored_children():
                node = node.explore_rand_child(root.creature)
                exit = True
            else:
                node = self.max_OLE(node)
            
 
        # add new state evaluation 
        state = node.game
        node.terminal_visits += 1 
        score = self.static_evaluator(state)
        node.value = node.value + score
       

        # update tree 
        while not node.is_root:
            
            node.visits += 1 
            node.sumResults = self.sum_results(node)
            node = node.parent 
            


    def turn(self, game):
        """
        Move forward one action and evaluate state 
        use only the top half of states to expand, 
        conduct random trials 
        """
        start = time.perf_counter()
        root = Node(None, None)
        root.creature = self 
        root.game = game.create_copy()

        for trial in range(self.simlations):
            self.run_simulation(root)
        end = time.perf_counter()
        self.times.append(end - start)

        return root.get_best_child().turn  
    
    def average_time(self):
        if len(self.times) == 0:
            return -1 
        else:
            return sum(self.times) / len(self.times)
    