import numpy as np
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import jsonpickle 
import math 


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

    plt.figure(figsize= (14,6))
    plt.title(title)
    plt.ylabel("Games Won")
    plt.xlabel("Agent used")
    plt.bar(agents, wins)
    plt.savefig(name + ".png")
    #plt.close() 

def display_indivual_graph(dict, key, name, title):
    agent_results = dict[key]

    xlabels = [] 
    yvalues = [] 

    for result in agent_results:
        xlabels.append(result["vs"])
        yvalues.append(result["wins"])
    
    plt.figure()
    plt.title(title) 
    plt.ylabel("Games Won")
    plt.xlabel("Opposing Agent")
    plt.bar(xlabels, yvalues)
    plt.savefig(name + ".png")
    #plt.close()

def empty_list(n):
    li = [] 

    for r in range(n):
        row = []
        for c in range(n):
            row.append(np.nan)
        li.append(row)
    
    return li 

def get_win_array(dict):
    agent_list = list(dict.keys()) 
    vs_list = list(dict.keys())
    win_list = empty_list(len(dict))

    for key in dict: 
        results = dict[key]
        results.pop() 
        r = agent_list.index(key)

        for game in results:
                # add to vs list if not alreay 
                if not game["vs"] in vs_list:
                    vs_list.append(game["vs"])
                c= vs_list.index(game["vs"])

                rate = game["wins"] / (game["wins"] +game["losses"] + game["ties"])
                win_list[r][c] = rate

    return agent_list, vs_list, win_list 




def get_graph_time(dict, name, title):
    total_dict = getAverageTime(dict)
    

    agents = total_dict.keys() 
    times = total_dict.values() 
    log_times = [math.log(time) for time in times]
    
    plt.figure(figsize= (14,6))
    plt.title(title) 
    plt.ylabel("Log of Average Time (seconds) Per Turn")
    plt.xlabel("Agent")
    plt.bar(agents, log_times)
    plt.savefig(name + ".png")
    #plt.close()

def create_heat_map(dict, name, title):
    agent_list, vs_list, results = get_win_array(dict)
    results = np.array(results)


    fig, ax = plt.subplots()
    im = ax.imshow(results,  cmap= "Greens", vmin=-0)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(agent_list)), labels=agent_list)
    ax.set_yticks(np.arange(len(vs_list)), labels=vs_list)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(agent_list)):
        for j in range(len(vs_list)):
            if results[i, j] >= 0:
                if results[i, j] > 0.5:
                    color = "w"
                else:
                    color = "black"
                formated_text = '{:.2f}'.format(results[i,j])
                text = ax.text(j, i, formated_text,
                            ha="center", va="center", color=color)
    
    #create color bar
    cbar = ax.figure.colorbar(im, ax=ax,)
    cbar.ax.set_ylabel("win rate", rotation=-90, va="bottom")
    ax.set_title(title)
    ax.set_ylabel("agent")
    ax.set_xlabel("opposing agent")
    fig.tight_layout()
    plt.savefig(name + ".png")
    #plt.close()




manual_file = open("TouramentResults2/random_results.txt", "r").read() 
results = jsonpickle.decode(manual_file)

create_heat_map(results, "TouramentResults2/ManualResults", "Win Rate of Agents From Monster Manual")

getWinGraph(results, "TouramentResults2/generalSuccess", "Agent Success With Entire Manual")
get_graph_time(results, "TouramentResults2/generalTime", "Agent Clock Time Using Entire Manual")

#display_indivual_graph(results, "AggressiveCreature", "AggressiveManualResults", "Success of Aggressive Agaisn't Other Agents")
#display_indivual_graph(results, "MonteCarloGameSearch", "MCGSManualResults", "Success of MCGS Agaisn't Other Agents")


player_file= open("TouramentResults2/player_results.txt", "r").read() 
player_results = jsonpickle.decode(player_file)
create_heat_map(player_results, "TouramentResults2/PlayerResults", "Win Rate of Agents From PCs")
getWinGraph(player_results, "TouramentResults2/playerSuccess", "Agent Success With Players")
get_graph_time(player_results, "TouramentResults2/playerTime", "Agent Clock Time Using Players") 

#display_indivual_graph(results, "AggressiveCreature", "AggressivePlayerResults", "Success of Aggressive Agaisn't Other Agents For Player Games")
#display_indivual_graph(results, "MonteCarloGameSearch", "MCGSPlayerResults", "Success of MCGS Agaisn't Other Agents For Player Games")
