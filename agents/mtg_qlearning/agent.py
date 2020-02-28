import time
import argparse

import cv2
import numpy as np

from environments.move_to_goal.move_to_goal import MoveToGoal


DEFAULT_BOARD_SIZE = (6, 10)


class Agent(object):

    def __init__(self, game: MoveToGoal):

        self.game = game
        self.q_table = np.random.uniform(low=-2, high=1, size=self.game.get_board_size())

    def produce_action(self):

        return np.random.randint(0, len(self.game.actions))


def main():
    parser = argparse.ArgumentParser(description="Q Learning agent that plays the MoveToGoal environment.")
    parser.add_argument("--board_size", type=int, nargs="*", default=DEFAULT_BOARD_SIZE)
    args = parser.parse_args()

    board_size = args.board_size
    if len(board_size) != 2:
        raise ValueError(f"The board size must be 2 values. "
                         f"Found ( {len(board_size)} ) values = {board_size}")

    test_game = MoveToGoal(board_size[0], board_size[1])
    test_game.prepare_game(player_pos=(0, 0), goal_pos=(board_size[0] - 1, board_size[1] - 1))

    test_agent = Agent(game=test_game)

    human_view = False
    while True:
        test_game.display_game()
        action = test_agent.produce_action()
        state, reward, done = test_game.step(action)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if done:
            break

        if human_view:
            time.sleep(.5)

        print(reward, state)


if __name__ == '__main__':
    main()
