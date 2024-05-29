
from PlayTestingEncounterFile import run_experiment 
from RuleBasedAgents import AggressiveCreature 
import random 
import numpy.random as npr
from MonsterManual import MONSTER_MANUAL
class EncounterChromosome:
    # randomly generate an encounter with 1 to 5 monsters 
    def __init__(self, party, monsters_to_select, ideal_difficulty, difficulty_stat = "normalized damage",  monsters = None, agent = AggressiveCreature, add_rate = 0.5, grid_size = 10):
        self.party = party 
        self.agent = agent 
        self.ideal_difficulty = ideal_difficulty
        self.monsters_to_select = monsters_to_select
        if monsters is None:
            self.monsters = []
            for i in range(random.randint(1, 5)):
                self.monsters.append(random.choice(monsters_to_select))
        else:
            self.monsters = monsters  
        
        self.add_rate = add_rate
        self.grid_size = grid_size
        self.difficulty_stat = difficulty_stat

    # randomly add a monster or remove a monster 
    def mutate(self):
        monsters = self.monsters[:]
        to_add = None 
        if len(self.monsters) <= 1:
            to_add = True 
        elif len(self.monsters) >= self.grid_size:
            to_add = False 
        else: 
            to_add = random.randrange(0, 1) < self.add_rate 
        

        if to_add:
            new_monster = random.choice(self.monsters_to_select)
            monsters.append(new_monster)
        else:
            monster = random.choice(monsters)
            monsters.remove(monster)
        
        return EncounterChromosome(self.party, self.monsters_to_select, self.ideal_difficulty, monsters=monsters, agent = self.agent, add_rate=self.add_rate, grid_size=self.grid_size, difficulty_stat = self.difficulty_stat)

    

    # shuffle monster list between two chromosomes 
    # assumes party is the same (most other parameters should be the same also)
    def cross_over(self, other):
        all_monsters = self.monsters + other.monsters 
        random.shuffle(all_monsters)
        index = round(len(all_monsters) / 2 )
        c1_monsters = all_monsters[0:index]
        c2_monsters = all_monsters[index:]
        new_monster_list = self.monsters_to_select 
        monsters_to_add = [m for m in other.monsters_to_select if not m in self.monsters_to_select]
        new_monster_list += monsters_to_add 

        child1 = EncounterChromosome(self.party, new_monster_list, self.ideal_difficulty, monsters=c1_monsters, agent = self.agent, add_rate=self.add_rate, grid_size=self.grid_size, difficulty_stat = self.difficulty_stat)
        child2 = EncounterChromosome(self.party, new_monster_list, other.ideal_difficulty, monsters=c2_monsters, agent = other.agent, add_rate=other.add_rate, grid_size=other.grid_size, difficulty_stat = other.difficulty_stat)

        return child1, child2 

    # run playtests and return how close 
    # it is to ideal difficulty 
    def fitness(self, trials = 10, debug = False):
        stats, game_log = run_experiment(self.agent, self.party, self.monsters, num_trials = trials, grid_size = self.grid_size)

        if debug:
            print(stats)

        return abs(stats[self.difficulty_stat] - self.ideal_difficulty)

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
        encounter = EncounterChromosome(party, monsters, ideal_difficulty)
        population.append((encounter.fitness(), encounter))
    
    sort_population(population)

    history = History()
    history.update(population)

    for gen in range(gens):

        if gen % 5 == 0 and debug:
            print("gen {} - top fitness:{}".format(gen, population[0][0]))
            print("\t", population[0][1].monsters)
        
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
    ideal_difficulty = 1

    encounter1 = EncounterChromosome(party, monsters, ideal_difficulty)
    encounter2 = EncounterChromosome(party, monsters, ideal_difficulty)

    print(encounter1.monsters)
    print(encounter2.monsters)

    mutant1 = encounter1.mutate()

    print("mutant:", mutant1.monsters)


    child1, child2 = encounter1.cross_over(encounter2)
    print("child1: ", child1.monsters)
    print("child2", child2.monsters)

    print(encounter1.fitness(debug=True))
    print(encounter1.fitness(debug=True))

    encounter, history = evolution(party, monsters, ideal_difficulty, 10, 30, 5, 1, 0.6)
    print(encounter.monsters)
    print(history.top_fitness)