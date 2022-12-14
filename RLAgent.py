from DnDToolkit import * 
from BasicAgents import *
import time  
from MonsterManual import * 
import math 
from GeneralAgentFunctions import * 
from ReinforcmentLearning import * 
from stable_baselines3 import A2C

class RLCreature(Creature):
    """
    Use reinforcement learning to make 
    decisions 

    OpenAIGym was used to create enviroment 
    Ac3 was used as reinforcement algorithm 
    
    """
    def __init__(self, ac, hp, speed, modifiers = Modifiers(), features = None, 
                    position = (0,0), name = "Creature", team = "neutral", actions = None, 
                    immunities = None, resistences = None, depths = [0, 10, 20, 30, 40, 40, 40], trimming_raito = 0.25,  debug= True, level = 0.5,
                    spell_manager = None, makes_death_saves = False):
        super().__init__(ac, hp, speed, modifiers, features, position, name, team, actions, immunities, resistences, level=level, 
                        spell_manager=spell_manager, makes_death_saves=makes_death_saves)
        self.depths = depths 
        self.debug = debug 
        self.times = []  
        self.trimming = trimming_raito 
        self.init = False 
        self.time_components = {} 
        for i in self.depths:
            self.time_components[i] = {"sim": 0, "copy": 0, "total": 0, "inst": 0}
        self.turn_lengths = [] 

    
    def turn(self, game):
        """
        Use RL models to choose actions 
        """
        start = time.perf_counter()
        options = self.avail_actions(game) 
        self.turn_lengths.append(len(options))
        if not self.init:
            self.env = DnDEnv(game, self)
            self.model = A2C('MlpPolicy', self.env, verbose=0)
            self.model.learn(total_timesteps=500) 
            self.init = True 
        else:
            self.env.set_starting(game)
            self.model.learn(total_timesteps=200) 

        obs = self.env.reset()
        action, states = self.model.predict(obs)
        action = action % len(options)

        end = time.perf_counter()
        self.times.append(end - start) 
     
        return options[action]
    
    def average_time(self):
        if len(self.times) == 0:
            return -1 
        else:
            return sum(self.times) / len(self.times)