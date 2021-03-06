#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Snake for Mate Light
====================

This is a clone of the well known snake game for Mate Light using pymlgame.
"""

__author__ = 'Ricardo Band'
__copyright__ = 'Copyright 2014, Ricardo Band'
__credits__ = ['Ricardo Band']
__license__ = 'MIT'
__version__ = '1.1.0'
__maintainer__ = 'Ricardo Band'
__email__ = 'me@xengi.de'
__status__ = 'Development'

import time
import random

import pymlgame

from snake import Snake, UP, DOWN, LEFT, RIGHT


class Game(object):
    """
    The main game class that holds the gameloop.
    """
    def __init__(self, mlhost, mlport, screen_width, screen_height):
        """
        Create a screen and define some game specific things.
        """
        pymlgame.init()
        self.screen = pymlgame.Screen(mlhost, mlport, screen_width, screen_height)
        self.clock = pymlgame.Clock(15)

        self.reset()

    def reset(self):
        part = (int(self.screen.width / 2), int(self.screen.height / 2))
        self.snake = Snake([(part[0] - 2, part[1]), (part[0] - 1, part[1]),
                            part], RIGHT, (self.screen.width, self.screen.height))
        self.gameover = False
        self.apple = self.generate_apple()
        self.apple_surface = pymlgame.Surface(1, 1)
        self.apple_surface.draw_dot((0, 0), pymlgame.GREEN)
        self.oldapple = self.apple
        self.score = 0
        self.highscore = self.get_highscore()

    def update(self):
        """
        Update the screens contents in every loop.
        """
        if not self.snake.move():
                    self.gameover = True

        if self.snake.get_pos() == self.apple:
                self.score += 1
                self.oldapple = self.apple
                self.apple = self.generate_apple()

    def render(self):
        """
        Send the current screen content to Mate Light.
        """
        self.screen.reset()

        # draw snake
        surface = pymlgame.Surface(self.screen.width, self.screen.height)
        for part in self.snake.parts:
            surface.draw_dot(part, pymlgame.RED)
        self.screen.blit(surface)

        # draw apple
        self.screen.blit(self.apple_surface, self.apple)

        if self.snake.parts[0] == self.oldapple:
            self.snake.grow = True
            self.oldapple = None

        self.screen.update()

        #TODO: accelerate every 5 points by 1 fps
        self.clock.tick()

    def handle_events(self):
        """
        Loop through all events.
        """
        for event in pymlgame.get_events():
            if event.type == pymlgame.E_NEWCTLR:
                print('new ctlr with uid:', event.uid)
            elif event.type == pymlgame.E_KEYDOWN:
                if event.button == pymlgame.CTLR_UP:
                    if self.snake.direction != DOWN:
                        self.snake.direction = UP
                elif event.button == pymlgame.CTLR_DOWN:
                    if self.snake.direction != UP:
                        self.snake.direction = DOWN
                elif event.button == pymlgame.CTLR_LEFT:
                    if self.snake.direction != RIGHT:
                        self.snake.direction = LEFT
                elif event.button == pymlgame.CTLR_RIGHT:
                    if self.snake.direction != LEFT:
                        self.snake.direction = RIGHT
            elif event.type == pymlgame.E_PING:
                print('ping from', event.uid)

    def gameloop(self):
        """
        A game loop that circles through the methods.
        """
        try:
            while True:
                while not self.gameover:
                    self.handle_events()
                    self.update()
                    self.render()
                print('game over - score:', self.score)
                print('current highscore:', self.highscore)
                if int(self.score) > int(self.highscore):
                    self.write_highscore()

                end = time.time() + 5
                while time.time() < end:
                    self.screen.reset()
                    self.screen.update()
                    self.clock.tick()
                self.reset()

        except KeyboardInterrupt:
            pass

    def generate_apple(self):
        return (random.randrange(self.screen.width),
                random.randrange(self.screen.height))

    def write_highscore(self):
        """
        Write new highscore to a file.
        """
        try:
            with open('highscore', 'w') as f:
                if f.writable():
                    f.writelines(str(self.score))
            return True
        except IOError:
            return False

    @staticmethod
    def get_highscore():
        """
        Reads the current highscore from a file.
        """
        highscore = 0
        try:
            with open('highscore', 'r') as f:
                highscore = f.readline()
        except IOError:
            pass
        return highscore


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Play Snake on your Matelight")
    parser.add_argument('host', help='remote host to connect to')
    parser.add_argument('-p', '--port', type=int, default=1337, help='remote port')
    parser.add_argument('--width', type=int, default=15, help='width of matelight')
    parser.add_argument('--height', type=int, default=16, help='height of matelight')

    args = parser.parse_args()
    #GAME = Game('127.0.0.1', 1337)
    GAME = Game(
        args.host,
        args.port,
        args.width,
        args.height,
    )
    GAME.gameloop()
