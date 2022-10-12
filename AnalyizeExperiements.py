import statistics
import jsonpickle
import matplotlib.pyplot as plt

def get_data():
    game_vals = {"Easy":[], "Medium":[], "Hard": [], "Deadly":[]}
    

    for i in range(8, 40):
        try: 
            file = open("PlayTestingResults/stats_game-"+ str(i) + ".txt")
            game_stats = jsonpickle.decode(file.read()) 
            damage_list = [game["total damage"] for game in game_stats["results"]] 
            health_list = [game["ending health"] for game in game_stats["results"]] 
            succ_list =   [game["success"] for game in game_stats["results"]] 
            sleep_list = [game["amount asleep"] for game in game_stats["results"]] 
            dead_list = [game["deaths"] for game in game_stats["results"]] 
            game_dict = {"difficulty": game_stats["difficulty"], "monsters":game_stats["monsters"], 
                            "damage": damage_list, "health": health_list, "success": succ_list, "asleep": sleep_list, 
                            "deaths": dead_list}
            game_vals[game_stats["difficulty"]].append(game_dict)
            file.close() 
        except:
            print("error in {}".format(i))
    
    return game_vals

def condense_results(game_data):
    cond_vals = {"Easy":[], "Medium":[], "Hard": [], "Deadly":[]}
    
    for key in game_data:
        damage_li = []
        health_li = [] 
        succ_li = [] 
        asleep_li = [] 
        dead_li = [] 

        for game in game_data[key]:
            damage_li += game["damage"]
            health_li += game["health"]
            succ_li += game["success"]
            asleep_li += game["asleep"]
            dead_li += game["deaths"]
        cond_vals[key] = {"damage": damage_li, "health": health_li, "success": succ_li, "asleep": asleep_li, "death": dead_li}
    
    return cond_vals 

def creat_box_plt(data_dict, attribute):

    
 
    easy = data_dict["Easy"][attribute]
    medium = data_dict["Medium"][attribute]
    hard = data_dict["Hard"][attribute]
    deadly= data_dict["Deadly"][attribute]
    
    box_plot_data=[easy, medium, hard, deadly]
    plt.boxplot(box_plot_data,patch_artist=True,labels=["easy", "medium", "hard", "deadly"])
    plt.savefig("PlayTestingGraphs/" + attribute +".png")

def get_statistics(data):
    stats = {"Easy":{}, "Medium":{}, "Hard": {}, "Deadly":{}}
    for key in data:
        for attibute in data[key]:
            m = statistics.mean(data[key][attibute])
            median = statistics.median(data[key][attibute])
            std = statistics.stdev(data[key][attibute])
            quant = statistics.quantiles(data[key][attibute]) 
            stats[key][attibute] = {"mean": m, "median": median, "stdev": std, "quantiles": quant}
        
    return stats 


            

vals = get_data()
print("Length easy: {}".format(len(vals["Easy"])))
print("Length medi: {}".format(len(vals["Medium"])))
print("Length hard: {}".format(len(vals["Hard"])))
print("Length dead: {}".format(len(vals["Deadly"])))

cond = condense_results(vals)
creat_box_plt(cond, "success")

stats = get_statistics(cond)

for key in stats:
    print(key + ":")
    print(stats[key]) 
    print("\n\n")
