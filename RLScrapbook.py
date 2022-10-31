import gym

from stable_baselines3 import A2C
from stable_baselines3.common.env_util import make_atari_env
from stable_baselines3.common.vec_env import VecFrameStack
from ReinforcmentLearning import DnDEnv
from tournament import * 
from stable_baselines3.common.env_checker import check_env


# There already exists an environment generator that will make and wrap atari environments correctly.

player, game = create_random_game()
env = DnDEnv(game, player)
#check_env(env)
# Stack 4 frames
#env = VecFrameStack(env, n_stack=4)

model = A2C('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=1000) 