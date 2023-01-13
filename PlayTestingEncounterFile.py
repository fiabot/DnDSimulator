import csv 
from DMGToolkit import * 
from RuleBasedAgents import * 
#from MonsterManual import * 
from ShyneAgent import TrimmingCreature
import functools
from multiprocessing import Pool 
import time 

PARTY_LIST = {} 

PARTY_LIST[5] = {"Balanced 1": ["Dwarf cleric" , "Elf wizard 2",  "Halfing rogue",  "Human fighter",  "Human figher 2"], \
                "Balanced 2": ['orc warlock', 'halfing ranger',' gnome sorcerer', 'human cleric', 'Human fighter'], \
                "Unbalanced 1" : ['elf wizard','gnome sorcerer', 'elf wizard 2', 'orc warlock', 'elf druid'],\
                "Unbalanced 2" : ['halfing ranger', 'halfing rogue','human fighter','human figher 2', "tiefling ranger"],\
                "Random" : ['human figher 2', 'elf druid', 'gnome sorcerer', 'human fighter','tiefling ranger'],\
                }

def get_rows_csv(filename):
    field_list = [] 
    rows = [] 
    # reading csv file
    with open(filename, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        
        # extracting field names through first row
        field_list = next(csvreader)
    
        # extracting each data row one by one
        for row in csvreader:
            rows.append(row)
    return field_list, rows




def run_experiment(agent_class, player_names, monster_names, num_trials = 10, grid_size = 7, round_limit = 20): 
    """
    run a single experiement given an agent class
    a set of player names 
    and a set of monster names 

    returns stat averages and stat log of games  
    """
   
    monster_stats = names_to_chars(monster_names)
    player_stats = names_to_chars(player_names)

        
    monsters = [create_creature(agent_class,monster) for monster in monster_stats] 
    players = [create_creature(agent_class, pc) for pc in player_stats]


    grid = Grid(grid_size, grid_size)
    
    player_pos, monster_pos = set_positions(len(players), len(monsters))

    game = Game(players, monsters, player_pos, monster_pos, grid)

    # run games 
    for game_num in range(num_trials):
        game.play_game(round_limit= round_limit) 
    
    game_log = game.stat_log
    average_stats = game.get_average_stats()

    return average_stats, game_log 

def get_monsters(row):
    """
    get monster names from a experiement rows 
    """
    monster_names = row[2:]
    monster_names = [monster for monster in monster_names if len(monster) > 0] # remove empty strings 
    return monster_names 


def run_experiment_file(rows, num_players, agent_class, num_trials = 20, debug = False, grid_size = 7, round_limit = 20): 
    party_sets = PARTY_LIST[num_players]
    fields = ["Encounter Code", "Number of Players", "DMG difficulty", "DMG xp"]
    encounter_results = {}

    for party in party_sets:
        fields += [party + " ave success", party + "ave damage"] 

        if debug: 
            print("Running party: {}.".format(party))

        for row in rows:
            code = row[0]
            if debug: 
                print("\t Running encounter: {}.".format(code))
            try: 
                monster_names = get_monsters(row)
                if not code in encounter_results:
                    encounter_results[code] = [code, row[1]]
                    encounter_results[code] += [predict_difficuly(monster_names, just_names = True), get_adjusted_xp(monster_names, just_names = True)]
            
                average, log = run_experiment(agent_class, party_sets[party], monster_names, num_trials = num_trials)
                encounter_results[code] += [average["success"], average["total damage"]]
            except Exception as e: 
                print(e)
                encounter_results[code] += [-1, -1]
    return fields, list(encounter_results.values())

def run_row(row, num_players, agent_class, num_trials = 20, debug = False, grid_size = 7, round_limit = 20): 
    party_sets = PARTY_LIST[num_players]

    encounter_results = {"Encounter Code": row[0]}
    encounter_results["Number of Players"] = num_players

    monster_names = get_monsters(row)

    encounter_results["DMG difficulty"] = predict_difficuly(monster_names, just_names = True)
    encounter_results["DMG xp"] = get_adjusted_xp(monster_names, just_names = True)
    if debug: 
        print("Running encounter: {}.".format(row[0]))

    for party in party_sets:
  

        try: 
            
        
            average, log = run_experiment(agent_class, party_sets[party], monster_names, num_trials = num_trials)
            encounter_results[party + " ave success"] = average["success"]
            encounter_results[party + "ave damage"] = average["total damage"]
             
        except Exception as e: 
            print(e)
            encounter_results[party + " ave success"] = -1 
            encounter_results[party + "ave damage"] = -1
            
    return encounter_results

def make_fields(num_players):
    fields = ["Encounter Code", "Number of Players", "DMG difficulty", "DMG xp"]
    party_sets = PARTY_LIST[num_players] 
    for party in party_sets:
        fields += [party + " ave success", party + "ave damage"] 
    
    return fields 

def results_to_row(fields, results):
    row = []
    for field in fields:
        row += [results[field]]
    
    return row 



def config_run_func(num_players, agent_class, num_trials = 20, debug = False, grid_size = 7, round_limit = 20):
    return functools.partial(run_row, num_players = num_players, agent_class = agent_class, num_trials = num_trials, 
                        debug = debug, grid_size= grid_size, round_limit = round_limit)


def run_parallel(num_processes, func, elements):
    """
    run function in parrallel
    with n processes and given element 
    list 
    """
    return_list = [] 
    with Pool(num_processes) as pool:
        # create a set of word hashes
        return_list = pool.map(func, elements)
    return return_list

def post_processes(fields, parallel_list):
    """
    extract fields and rows 
    from parallel results 
    """
    
    rows = [results_to_row(fields, li) for li in parallel_list]
    return rows 

def run_experiment_parallel(rows, num_players, agent_class, num_trials = 20, debug = False, grid_size = 7, round_limit = 20, num_processes = 4):
    foo = config_run_func(num_players, agent_class, num_trials, debug, grid_size, round_limit) 
    fields = make_fields(num_players)
    results = run_parallel(num_processes, foo, rows)
    return fields, post_processes(fields, results)

def write_to_file(header, data, filename):
    # open the file in the write mode
    with open(filename, 'w') as f:
        # create the csv writer
        writer = csv.writer(f)

        # write the header 
        writer.writerow(header)

        for row in data:
            writer.writerow(row)


if __name__ == "__main__":
    filename = "PlayTestingExperimentFiles/EncounterList3.csv"
    fields, rows = get_rows_csv(filename)
    start = time.perf_counter()
    fields, rows = run_experiment_parallel(rows, 5, TrimmingCreature, debug = False, num_trials = 10) 
    end = time.perf_counter()
    print(end - start)
    write_to_file(fields, rows, "PlayTestingExperimentFiles/TrimingTest2.csv")
    #foo = config_run_func(5, AggressiveCreature, debug = True)
    
    #foo(rows)


