from typing import Iterable
import gym 
from gym import spaces 
from DnDToolkit import * 
from CreatureClasses import * 
from GeneralAgentFunctions import * 
import jsonpickle 
from tournament import * 
import math
import sys 

MAX_ACTIONS = 10 
MAX_INT  = 10 ** 3

def game_hash(game: Game):
    creature_list = [] 
    for i in game.players + game.monsters:
        li = [i.name, i.hp, i.position]
        creature_list.append(li) 
    return str(creature_list)




    


class DnDEnv(gym.Env):
    def __init__(self, starting_game: Game, creature: Creature, depth_limit = 20) -> None:
        self.starting_game = starting_game.create_copy()
        self.game = self.starting_game 
        self.creature = starting_game.get_creature(creature.name)

        self.observation_space = spaces.Discrete(MAX_INT)
        self.action_space = spaces.Discrete(MAX_ACTIONS) 
        self.depth_limit = depth_limit 
        self.depth = 0 
        self.states = {} 
        self.next_state = 0 

    def convertFromState(self, game):
        hash = game_hash(game)
        if hash in self.states:
            return self.states[hash]
        else:
            self.states[hash] = self.next_state
            self.next_state += 1 
            self.next_state = self.next_state % MAX_INT
            return self.states[hash]

    def set_starting(self, game):
        self.starting_game = game.create_copy()
        self.game = self.starting_game 

    def reset(self, seed=None, options=None):

        self.game = self.starting_game 
        self.depth = 0  

        return self.convertFromState(self.game)

    def step(self, action_index):
        self.depth += 1 
        creature = self.game.next_creature()
        avail_actions = creature.avail_actions(self.game) 
        action_index = action_index % len(avail_actions)
        action = avail_actions[action_index]
        self.game = forward_action(action, creature.name, self.game) 
        simulate_game(self.game, self.depth_limit)

        while not self.game.is_terminal() and self.game.next_creature().name != self.creature.name: 
            one_step(self.game) 
        
        observation = self.convertFromState(self.game)
        terminated = self.game.is_terminal()
        reward = heuristic(self.creature, self.game)
        done = terminated or self.depth > self.depth_limit 
        info = {}

        return observation, reward, done, info  
