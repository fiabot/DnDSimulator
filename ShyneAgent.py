from DnDToolkit import * 
from BasicAgents import *
import time  
from MonsterManual import * 
import math 

class ShyneCreature(Creature):
    def __init__(self, ac, hp, speed, modifiers = Modifiers(), features = None, 
                    position = (0,0), name = "Creature", team = "neutral", actions = None, 
                    immunities = None, resistences = None, depths = [0, 10, 20, 30, 40], debug= True, level = 0.5):
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level = level)
        self.depths = depths 
        self.debug = debug 
        self.times = []  
        self.time_components = {} 
        for i in self.depths:
            self.time_components[i] = {"sim": 0, "copy": 0, "total": 0, "inst": 0}
    
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

    def create_game_copy(self, map, order):
        """
        create a copy of the game 
        TODO: Move this out of agent 
        """
 
        order_copy = copy.deepcopy(order)
        map_copy = copy.deepcopy(map)

        #this may be the jankyiest solution but..... 
        map_copy.clear_grid() 
        map_copy.place_pieces(order_copy)

        return map_copy, order_copy


        
    def simulate_game(self, game, depth):
        """
        simulate a game given depth 
        return the resulting map 

        initiative is the creature going 
        next 

        Assumes that game is a copy 
        """
        cur_depth = 0 
        

        while cur_depth < depth:
            creature = game.update_init() 
            turn = self.decide_action(game, creature)
            game.next_turn(creature, turn)
            
            cur_depth += 1 
        return game
    
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

            cutoff = math.ceil(len(options_evaluations) / 2)

            options_evaluations = options_evaluations[:cutoff]
        
        end = time.perf_counter()
        if self.debug:
            self.times.append(end - start) 
     
        return options_evaluations[0][1]
    
    def average_time(self):
        return sum(self.times) / len(self.times) 
    
    def display_times(self):
        print("Average total turn time: {}".format(self.average_time()))
        for depth in self.time_components:
            times = self.time_components[depth]
            print("For depth: {}".format(depth))
            print("\tAverage Simulation Time: {}".format(times["total"] / times["inst"]))
            print("\tAverage Copying Time   : {}".format(times["copy"] / times["inst"]))
            print("\tAverage Future Time    : {}".format(times["sim"] / times["inst"]))
            print("Sums: full : {}, copying : {}, future sim: {}".format(times["total"], times["copy"], times["sim"]))


if __name__ == "__main__":
    map = Grid(10, 10, space=1)
    shyne_wolf = create_creature(ShyneCreature, direWolf)
    players = [shyne_wolf] + [create_creature(ShyneCreature, direWolf), create_creature(ShyneCreature, direWolf), create_creature(ShyneCreature, direWolf)]
    rand_wolf = create_creature(AggressiveCreature, direWolf)
    monsters = [rand_wolf] + [create_creature(AggressiveCreature, direWolf), create_creature(AggressiveCreature, direWolf), create_creature(AggressiveCreature, direWolf)]
    print(players)
    game = Game(players, monsters, [(0,0), (1, 0), (2, 0), (3, 0)], [(9,9), (8,9), (7, 9), (6, 9)], map = map)

    game.play_game() 
    shyne_wolf.display_times() 
    
