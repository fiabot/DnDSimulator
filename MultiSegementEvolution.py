
from PlayTestingEncounterFile import run_experiment, names_to_chars, create_creature
from RuleBasedAgents import AggressiveCreature 
import random 
import numpy.random as npr
from MonsterManual import MONSTER_MANUAL
from DnDToolkit import * 
from copy import deepcopy 
import jsonpickle 

def run_experiment(agent_class, player_names, stages, num_trials = 10, round_limit = 20): 
    """
    run a single experiement given an agent class
    a set of player names 
    and a set of monster names 

    returns stat averages and stat log of games  
    """
   
    
    

    games = []
    all_monsters = []

    player_stats = names_to_chars(player_names)
    players = [create_creature(agent_class, pc) for pc in player_stats]

    for stage in stages: 


        monster_names = stage["names"]
        grid_size = stage["size"]

        monster_stats = names_to_chars(monster_names)
        monsters = [create_creature(agent_class,monster) for monster in monster_stats] 
        all_monsters += monsters
        


        grid = Grid(grid_size, grid_size)
        
        player_pos, monster_pos = set_positions(len(players), len(monsters))

        game = Game(players, monsters, player_pos, monster_pos, grid)
        games.append(game)

    # run games 
    for game_num in range(1):
        for game in games:
            game.play_game(round_limit= round_limit, long_rest = False, debug=False ) 
        
        for player in players: 
            player.long_rest()
        for monster in monsters:
            monster.long_rest()
    
    game_logs = [game.stat_log for game in games]
    average_stats =[ game.get_average_stats() for game in games]

    return average_stats, game_logs 


class StagesChromosome:
    # randomly generate multiple stages of encounters each with 1 to 5 monsters 
    def __init__(self, party, monsters_to_select, ideal_difficulties, difficulty_stat = "normalized damage",  stages= None, agent = AggressiveCreature, add_rate = 0.5, grid_sizes = None):
        if grid_sizes == None:
            self.grid_sizes = [10] * len(ideal_difficulties)
        else:
            self.grid_sizes = grid_sizes
        self.party = party 
        self.agent = agent 
        self.ideal_difficulties = ideal_difficulties
        self.monsters_to_select = monsters_to_select
        if stages is None:
            self.stages = []
            for i in range(len(ideal_difficulties)):
                monsters = []
                for j in range(random.randint(1, 5)):
                    monsters.append(random.choice(monsters_to_select))
                stage = {"names":monsters, "size": self.grid_sizes[i]}
                self.stages.append(stage)
        else:
            self.stages = stages  
        
        self.add_rate = add_rate
        self.difficulty_stat = difficulty_stat

    # randomly add a monster or remove a monster 
    def mutate(self, amount = 3):
        stages = deepcopy(self.stages)
        for i in range(amount):
            index = random.randint(0, len(stages) - 1)
            monsters = stages[index]["names"]
            to_add = None 
            if len(monsters) <= 1:
                to_add = True 
            elif len(monsters) >= stages[index]["size"]:
                to_add = False 
            else: 
                to_add = random.randrange(0, 1) < self.add_rate 
            

            if to_add:
                new_monster = random.choice(self.monsters_to_select)
                monsters.append(new_monster)
            else:
                monster = random.choice(monsters)
                monsters.remove(monster)
        
        return StagesChromosome(self.party, self.monsters_to_select, self.ideal_difficulties, stages=stages, agent = self.agent, add_rate=self.add_rate, grid_sizes=self.grid_sizes, difficulty_stat = self.difficulty_stat)

    def __str__(self):
        num  = 1 
        s = ""
        for stage in self.stages:
            s += "Stage: {}\n".format(num)
            for name in stage["names"]:
                s += "\t{}\n".format(name)
            s+= "\tgrid size:{}\n".format(self.grid_sizes[num -1])
            num += 1 
        
        return s
    

    

    # shuffle monster list between two chromosomes 
    # assumes party and stage size are the same 
    def cross_over(self, other):
        my_stages = deepcopy(self.stages)
        their_stages = deepcopy(other.stages)

        child1_stages = []
        child2_stages = []
        

        for i in range(len(my_stages)):
            first = decide(0.5)

            if first:
                child1_stages.append(my_stages[i])
                child2_stages.append(their_stages[i])
            else:
                child2_stages.append(my_stages[i])
                child1_stages.append(their_stages[i])
        
        child1 = StagesChromosome(self.party, self.monsters_to_select, self.ideal_difficulties, stages=child1_stages, agent = self.agent, add_rate=self.add_rate, grid_sizes=self.grid_sizes, difficulty_stat = self.difficulty_stat)
        child2 = StagesChromosome(self.party, self.monsters_to_select, self.ideal_difficulties, stages=child2_stages, agent = self.agent, add_rate=self.add_rate, grid_sizes=self.grid_sizes, difficulty_stat = self.difficulty_stat)

        return child1, child2
    # run playtests and return how close 
    # it is to ideal difficulty 
    def fitness(self, trials = 10, debug = False):
        stats, game_log = run_experiment(self.agent, self.party, self.stages, num_trials = trials)

        if debug:
            print(stats)

        total_difference = 0
        i = 0 
        for diff in self.ideal_difficulties:
            total_difference +=  abs(stats[i][self.difficulty_stat] - diff)
            i += 1 
        return total_difference

def decide(rate):
  return random.random() < rate

# minimize selection 
def select(population):
    m = sum([c[0] for c in population])
    
    if(m == 0):
      selection_probs = [1/len(population) for c in population]
    else:
      inverse = [(1 - (c[0]/m)) for c in population]
      inverse_sum = sum(inverse)
      selection_probs = [i / inverse_sum for i in inverse]
    return population[npr.choice(len(population), p=selection_probs)]

def sort_population(population):
    population.sort(reverse= False, key = lambda a: a[0])

class History:
    def __init__(self):
        self.populations = []
        self.top_fitness = []
    def update(self, population):
        self.populations.append(population)
        self.top_fitness.append(population[0][0])


def evolution(party, monsters, ideal_difficulty, gens, popsize, eltistism, x_rate, mut_rate, debug= True):

    # intial popultion 
    population = []
    for i in range(popsize):
        encounter = StagesChromosome(party, monsters, ideal_difficulty)
        population.append((encounter.fitness(), encounter))
    
    sort_population(population)

    history = History()
    history.update(population)

    for gen in range(gens):

        if gen % 5 == 0 and debug:
            print("gen {} - top fitness:{}".format(gen, population[0][0]))
            print("\t", str(population[0][1]))
        
        new_pop = population[:eltistism]

        while len(new_pop) < popsize: 

            parent1 = select(population)[1]
            parent2 = select(population)[1]

            if(decide(mut_rate)):
                parent1 = parent1.mutate()
            
            if (decide(mut_rate)):
                parent2 = parent2.mutate()

            if decide(x_rate):
                child1, child2 = parent1.cross_over(parent2)
            else: 
                child1 = parent1 
                child2 = parent2 
            
            new_pop.append((child1.fitness(), child1))
            if len(new_pop) < popsize:
                new_pop.append((child2.fitness(), child2))
        
        population = new_pop 
        sort_population(population)
        history.update(population)
            
    return population[0][1], history 


if __name__ == "__main__":
    party =  ["Dwarf cleric" , "Elf wizard 2",  "Halfing rogue",  "Human fighter",  "Human figher 2"] 
    monsters = list(MONSTER_MANUAL.keys())
    ideal_difficulty = [0.2, 0.4, 0.6]

    """stages = [{"names": ["bandit", "bandit"], "size":10}, {"names": ["gray ooze"], "size":10}, {"names": ["noble"], "size":10}]

    stats, logs = run_experiment(AggressiveCreature, party, stages)
    print(len(stats))
    print(stats)"""

    encounter1 = StagesChromosome(party, monsters, ideal_difficulty)
    encounter2 = StagesChromosome(party, monsters, ideal_difficulty)

    print("encounter1")
    print(str(encounter1))
    print("encounter2")
    print(str(encounter2))
    print("\n\n")

    mutant1 = encounter1.mutate()

    print("mutant:")
    print(str(mutant1))
    print("\n\n")


    child1, child2 = encounter1.cross_over(encounter2)
    print("child1: \n", str(child1))
    print("child2", str(child2))
    print("\n\n")

    print(encounter1.fitness(debug=True))
    print(encounter1.fitness(debug=True))

    encounter, history = evolution(party, monsters, ideal_difficulty, 100, 300, 5, 1, 0.6)
    print(encounter)
    print(history.top_fitness)

    folder = "EvolutionTests/StageTest2g"

    encounter_json = jsonpickle.encode(encounter)
    history_json = jsonpickle.encode(history)

    file1 = open(folder + "/history.json", "w")
    file1.write(history_json)
    file1.close()

    file2 = open(folder + "/encounter.json", "w")
    file2.write(encounter_json)
    file2.close()