"""
Example.py
Jared Weinstein

An incredibly simple demonstration of an Pycolab environment
that contains multiple agents receiving unique actions and
rewards.

Major Change: Actions and Rewards become indexed lists
              game.play( [ LEFT, RIGHT ] )

              Every agent with a matching INDEX value receives
              the corresponding action. INDEX is determined by
              the value passed upon Partial(...) initialization.

              No safety checks are done to ensure that action and
              reward lists have the correct length. Please
              behave responsibly.
"""

import curses
import sys
import enum
import pdb
import argparse

import numpy as np

from pycolab import ascii_art, human_ui
from pycolab.prefab_parts import sprites

GAME_ART = ['#   0                #',
            '#             1      #']

def make_game():
    """Builds and returns a sample environment"""
    return ascii_art.ascii_art_to_game(
            GAME_ART,
            what_lies_beneath=' ',
            sprites= {
                '0': ascii_art.Partial(PlayerSprite, 0, 2),
                '1': ascii_art.Partial(PlayerSprite, 1, 2) }
            )

class Actions(enum.IntEnum):
    """ Actions for the player """
    STAY = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class RewardAgent(sprites.MazeWalker):
    """ Sprite representing any player with unique actions and rewards """

    def __init__(self, corner, position, character, index, n_unique):
        self.index = index
        self.n_unique = n_unique

        super(RewardAgent, self).__init__(corner, position, character, impassable='#')

    def update(self, actions, board, layers, backdrop, things, the_plot):
        raise NotImplementedError

    def reward(self, plot, value):
        reward = np.zeros(self.n_unique)
        reward[self.index] = value
        plot.add_reward(reward)


class PlayerSprite(RewardAgent):
    """ Sprite representing the player """

    def __init__(self, corner, position, character, index, n_unique):
        super(PlayerSprite, self).__init__(corner, position, character, index, n_unique)

    def update(self, actions, board, layers, backdrop, things, the_plot):
        del layers, backdrop, things # unused

        if actions == None:
            action = Actions.STAY
        else:
            action = actions[self.index]
        del actions

        # action update
        if action == Actions.LEFT:
            self._west(board, the_plot)
        elif action == Actions.RIGHT:
            self._east(board, the_plot)

        # distribute reward
        if self.position[1] == 1:
            self.reward(the_plot, 1)
            the_plot.terminate_episode()
        elif self.position[1] == (self.corner[1] - 2):
            self.reward(the_plot, 100)
            the_plot.terminate_episode()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Basic env to demonstrate pycolab to RLlib connection.')
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    del sys.argv

    game = make_game()

    if args.live:
        ui = human_ui.CursesUi(keys_to_actions=
                {
                    curses.KEY_LEFT: [Actions.LEFT, Actions.STAY],
                    curses.KEY_RIGHT: [Actions.STAY, Actions.RIGHT],
                    -1: [Actions.STAY, Actions.STAY]
                },
                delay=200)
        ui.play(game)
        sys.exit()

    if not args.live:
        game.its_showtime()
        while not game.game_over:
            board, reward, discount = game.play([Actions.LEFT, Actions.STAY])
