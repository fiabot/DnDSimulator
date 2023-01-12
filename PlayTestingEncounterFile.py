import csv 
from DMGToolkit import * 
from RuleBasedAgents import * 
#from MonsterManual import * 
from ShyneAgent import TrimmingCreature


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




def run_experiment(agent_class, player_names, monster_names, num_trials = 20, grid_size = 7, round_limit = 20): 
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


def run_experiment_file(rows, num_players, agent_class, num_trials = 20): 
    party_sets = PARTY_LIST[num_players]
    fields = ["Enconter Code", "Number of Players", "DMG difficulty", "DMG xp"]
    encounter_results = {}

    for party in party_sets:
        fields += [party + " ave success", party + "ave damage"] 

        for row in rows:
            code = row[0]
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
    fields, rows = run_experiment_file(rows, 5, AggressiveCreature) 
    write_to_file(fields, rows, "PlayTestingExperimentFiles/AggressiveTest1.csv")

