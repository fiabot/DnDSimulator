import matplotlib.pyplot as plt 
import jsonpickle 


def getTotalWins(dict):
    totals = {} 
    for key in dict:
        s = 0 
        for game in dict[key]:
            s += game["wins"]
        totals[key] = s
    return totals 

def getAverageTime(dict):
    totals = {} 
    for key in dict:
        s = 0 
        i = 0 
        for game in dict[key]:
            s += game["times"]
            i += 1 
        totals[key] = s / i 
    return totals 

def getWinGraph(dict, name, title):
    total_dict = getTotalWins(dict)

    agents = total_dict.keys() 
    wins = total_dict.values() 

    plt.figure(figsize =(10, 7))
    plt.title(title)
    plt.ylabel("Games Won")
    plt.xlabel("Agent used")
    plt.bar(agents, wins)
    plt.savefig(name + ".png")
    plt.close() 

def display_indivual_graph(dict, key, name, title):
    agent_results = dict[key]

    xlabels = [] 
    yvalues = [] 

    for result in agent_results:
        xlabels.append(result["vs"])
        yvalues.append(result["wins"])
    
    plt.figure(figsize =(10, 7))
    plt.title(title) 
    plt.ylabel("Games Won")
    plt.xlabel("Opposing Agent")
    plt.bar(xlabels, yvalues)
    plt.savefig(name + ".png")

def get_graph_time(dict, name, title):
    total_dict = getAverageTime(dict)

    agents = total_dict.keys() 
    wins = total_dict.values() 

    plt.figure(figsize =(10, 7))
    plt.title(title) 
    plt.ylabel("Average Time (seconds) Per Turn")
    plt.xlabel("Agent")
    plt.bar(agents, wins)
    plt.savefig(name + ".png")




manual_results = open("random_results.txt", "r").read() 
results = jsonpickle.decode(manual_results)
getWinGraph(results, "generalSuccess", "Agent Success With Entire Manual")
get_graph_time(results, "generalTime", "Agent Clock Time Using Entire Manual")

display_indivual_graph(results, "AggressiveCreature", "AggressiveManualResults", "Success of Aggressive Agaisn't Other Agents")
display_indivual_graph(results, "MonteCarloGameSearch", "MCGSManualResults", "Success of MCGS Agaisn't Other Agents")


manual_results = open("player_results.txt", "r").read() 
results = jsonpickle.decode(manual_results)
getWinGraph(results, "playerSuccess", "Agent Success With Players")
get_graph_time(results, "playerTime", "Agent Clock Time Using Players") 

display_indivual_graph(results, "AggressiveCreature", "AggressivePlayerResults", "Success of Aggressive Agaisn't Other Agents For Player Games")
display_indivual_graph(results, "MonteCarloGameSearch", "MCGSPlayerResults", "Success of MCGS Agaisn't Other Agents For Player Games")
