import time
import logging

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style

from environments.move_to_goal.move_to_goal import MoveToGoal


logger = logging.getLogger()
logger.setLevel(logging.INFO)

style.use("ggplot")


class MoveToGoalQAgent(object):

    def __init__(self, game: MoveToGoal):

        self.game = game
        self.board_size = self.game.get_board_size()
        self.q_table = self.generate_q_table()

    def generate_q_table(self):

        table_size = []
        for i in range(0, self.game.state_space, 2):
            table_size.append(self.board_size[0])
            table_size.append(self.board_size[1])
        table_size.append(len(self.game.actions))

        return np.random.uniform(low=-2, high=0, size=table_size)

    def produce_action(self, state: tuple):
        action = np.argmax(self.q_table[state])
        return action

    def train_agent(self, episodes: int=10_000, epsilon: float=1, plot_game: bool=False,
                    show_every: int=None, learning_rate: float=0.1, discount: float=0.95,
                    cycles: int=4):

        episodes_counter = 0
        total_episodes = episodes * cycles
        end_epsilon_decay = episodes // 2
        epsilon_decay_value = epsilon / (end_epsilon_decay - 1)
        episodes_wins = []
        episode_rewards = []
        if show_every is None:
            show_every = int(total_episodes * 0.1)

        logger.info("Starting training...")
        start_time = time.time()
        start_epsilon = epsilon
        for cycle in range(cycles):
            epsilon = start_epsilon

            for episode in range(episodes):

                self.game.prepare_game()
                if not episodes_counter % show_every and episodes_counter > 0:
                    logger.info("#########################")
                    logger.info(f"Showing episode N° {episode}/{episodes} of cycle {cycle}/{cycles}")
                    logger.info(f"Epsilon is {epsilon}")
                    logger.info(f"Last {show_every} episodes reward mean: {np.mean(episode_rewards[-show_every:])}")
                    batch_wins = np.sum(episodes_wins[-show_every:])
                    logger.info(f"Wins in last {show_every} episodes = {batch_wins}")
                    logger.info(f"Batch time = {time.time() - start_time} sec")
                    show = True
                    start_time = time.time()
                else:
                    show = False

                episode_reward = 0
                done = False
                while not done:

                    if show and plot_game:
                        self.game.display_game(f"Episode {episode}")
                        time.sleep(.01)

                    new_board_state, reward, done = self.training_step(epsilon, learning_rate, discount)

                    if done:
                        episodes_wins.append(reward == self.game.goal_reward)

                    episode_reward += reward

                if end_epsilon_decay >= episode >= 0:
                    epsilon -= epsilon_decay_value

                episode_rewards.append(episode_reward)
                episodes_counter += 1

        moving_avg = np.convolve(episode_rewards, np.ones((show_every,)) / show_every, mode='valid')

        self.plot_training_info(moving_avg)

    def training_step(self, epsilon, learning_rate, discount):

        board_state = self.game.get_state()

        if np.random.random() > epsilon:
            action = self.produce_action(board_state)
        else:
            action = np.random.randint(0, len(self.game.actions))
        new_board_state, reward, done = self.game.step(player_action=action)

        if done:
            self.q_table[board_state + (action,)] = reward
        else:
            max_future_q = np.max(self.q_table[new_board_state])
            current_q = self.q_table[board_state + (action,)]

            new_q = (1 - learning_rate) * current_q + learning_rate * (reward + discount * max_future_q)

            self.q_table[board_state + (action,)] = new_q

        return new_board_state, reward, done

    @staticmethod
    def plot_training_info(moving_avg: np.array):
        plt.figure(figsize=(5, 5))
        # Moving average plot

        plt.plot([i for i in range(len(moving_avg))], moving_avg)
        plt.ylabel(f"Reward")
        plt.xlabel("Episode #")
        plt.title("Reward moving average")

        plt.show()
