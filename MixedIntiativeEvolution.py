
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


        monster_names = stage["names"] + stage["lockedMons"]
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


class MI_StagesChromosome:
    # randomly generate multiple stages of encounters each with 1 to 5 monsters 
    def __init__(self, party, stage_settings, difficulty_stat = "normalized damage",  stages= None, agent = AggressiveCreature, add_rate = 0.5, grid_sizes = None):
        ideal_difficulties = [float(stage["difficulty"]) for stage in stage_settings]
        if grid_sizes == None:
            self.grid_sizes = [10] * len(ideal_difficulties)
        else:
            self.grid_sizes = grid_sizes
        self.party = party 
        self.agent = agent 
        self.ideal_difficulties = ideal_difficulties
        self.stage_settings = stage_settings
        #self.monsters_to_select =[stage["possMons"] for stage in stage_settings]
        if stages is None:
            self.stages = []
            i = 0 
            for stage in stage_settings:
                monsters = []
                stage["minMons"] = int(stage["minMons"])
                stage["maxMons"] = int(stage["maxMons"])
                stage["difficulty"] = float(stage["difficulty"])
                for j in range(random.randint(stage["minMons"], stage["maxMons"])):
                    monsters.append(random.choice(stage["possMons"]))
                stage = {"names":monsters, "lockedMons": stage["lockedMons"], "size": self.grid_sizes[i]}
                self.stages.append(stage)
                i += 1 
        else:
            self.stages = stages  
        
        self.add_rate = add_rate
        self.difficulty_stat = difficulty_stat

    # randomly add a monster or remove a monster 
    def mutate(self, amount = 3):
        stages = deepcopy(self.stages)
        for i in range(amount):
            index = random.randint(0, len(stages) - 1)
            settings = self.stage_settings[index]
            monsters = stages[index]["names"]
            to_add = None 
            if len(monsters) <= settings["minMons"]:
                to_add = True 
            elif len(monsters) >= settings["maxMons"]:
                to_add = False 
            else: 
                to_add = random.randrange(0, 1) < self.add_rate 
            

            if to_add:
                new_monster = random.choice(settings["possMons"])
                monsters.append(new_monster)
            else:
                monster = random.choice(monsters)
                monsters.remove(monster)
        
        return MI_StagesChromosome(self.party, self.stage_settings, stages=stages, agent = self.agent, add_rate=self.add_rate, grid_sizes=self.grid_sizes, difficulty_stat = self.difficulty_stat)

    def __str__(self):
        num  = 1 
        s = ""
        for stage in self.stages:
            s += "Stage: {}\n".format(num)
            s += "\tlocked mons\n"
            for name in stage["lockedMons"]:
                s += "\t\t{}\n".format(name)
            s += "\tadded mons\n"
            for name in stage["names"]:
                s += "\t\t{}\n".format(name)
            s+= "\tgrid size:{}\n".format(stage["size"])
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
        
        child1 = MI_StagesChromosome(self.party, self.stage_settings,  stages=child1_stages, agent = self.agent, add_rate=self.add_rate, grid_sizes=self.grid_sizes, difficulty_stat = self.difficulty_stat)
        child2 = MI_StagesChromosome(self.party, self.stage_settings, stages=child2_stages, agent = self.agent, add_rate=self.add_rate, grid_sizes=self.grid_sizes, difficulty_stat = self.difficulty_stat)

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


def mi_evolution(party, stage_settings, gens, popsize, eltistism, x_rate, mut_rate, debug= True):

    # intial popultion 
    population = []
    for i in range(popsize):
        encounter = MI_StagesChromosome(party, stage_settings)
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
            
    return population[0], history 


if __name__ == "__main__":
    party =  ["Dwarf cleric" , "Elf wizard 2",  "Halfing rogue",  "Human fighter",  "Human figher 2"] 
    monsters = list(MONSTER_MANUAL.keys())
    ideal_difficulty = [0.2, 0.4, 0.6]

    stage_settings =[ {
        "lockedMons": ["bandit", "dire wolf"], 
        "possMons": monsters,
        "minMons" : 2 , 
        "maxMons": 3 , 
        "difficulty": 0.3 

    }, {
        "lockedMons": ["camel"], 
        "possMons": monsters,
        "minMons" : 4 , 
        "maxMons": 6 , 
        "difficulty": 0.3 

    }  ]
    """stages = [{"names": ["bandit", "bandit"], "size":10}, {"names": ["gray ooze"], "size":10}, {"names": ["noble"], "size":10}]

    stats, logs = run_experiment(AggressiveCreature, party, stages)
    print(len(stats))
    print(stats)"""

    encounter1 = MI_StagesChromosome(party, stage_settings)
    encounter2 = MI_StagesChromosome(party, stage_settings)

    print("encounter1")
    print(str(encounter1))

    print(encounter1.fitness(debug=True))
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

    encounter, history = mi_evolution(party, stage_settings, 10, 10, 5, 1, 0.6)
    print(encounter[1])
    print(history.top_fitness)

    """folder = "EvolutionTests/StageTest2g"

    encounter_json = jsonpickle.encode(encounter)
    history_json = jsonpickle.encode(history)

    file1 = open(folder + "/history.json", "w")
    file1.write(history_json)
    file1.close()

    file2 = open(folder + "/encounter.json", "w")
    file2.write(encounter_json)
    file2.close()"""