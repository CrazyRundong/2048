# -*- coding: utf-8 -*-
# Rundong Li, UESTC

import pygame, sys, random
from pygame.locals import *
from enum import Enum

BOARD_WIDTH = 4
BOARD_HEIGHT = 4
BOX_SIZE = 100
MARGIN_SIZE = 20
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 640
MAX_SCORE = 2048
INIT_SCORE = 2
FPS = 30

X_MARGIN = int((WINDOW_WIDTH - (BOARD_WIDTH * (BOX_SIZE + MARGIN_SIZE))) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - (BOARD_HEIGHT * (BOX_SIZE + MARGIN_SIZE))) / 2)


class Direction(Enum):
    Up = 0
    Down = 1
    Left = 2
    Right = 3

SWITCHER = {  # idx_boundary, idx_slide_start, idx_step, attr_name (col/line), attr_name (elem), range of another attr
            Direction.Up: [0, BOARD_HEIGHT, 1, 'coordinate_x', 'coordinate_y', BOARD_WIDTH],
            Direction.Down: [BOARD_HEIGHT - 1, -1, -1, 'coordinate_x', 'coordinate_y', BOARD_WIDTH],
            Direction.Left: [0, BOARD_WIDTH, 1, 'coordinate_y', 'coordinate_x', BOARD_HEIGHT],
            Direction.Right: [BOARD_WIDTH - 1, -1, -1, 'coordinate_y', 'coordinate_x', BOARD_HEIGHT],
        }


class Block:
    def __init__(self, x=random.randint(0, 3), y=random.randint(0, 3)):
        self.coordinate_x = x
        self.coordinate_y = y
        self.score = INIT_SCORE
        self.moved = False
        self.slide_enable = True
        self.next_coordinate_x = x
        self.next_coordinate_y = y


class Board:
    def __init__(self):
        self.blocks = [Block(), ]
        self.max_score = max([block.score for block in self.blocks])
        self.next_direction = Direction.Up

    def handle_block_slide(self, direction):
        self.next_direction = direction
        # check each row/column (depend on direction)
        # TODO(Rundong) loop below can be optimised
        for line_col_idx in range(SWITCHER[direction][5]):
            # blocks in same row/column, idx in current row/column
            current_blocks = [[block, getattr(block, SWITCHER[direction][4])] for block in self.blocks if
                              getattr(block, SWITCHER[direction][3]) == line_col_idx]
            # search: [idx_boundary -> idx_move_start) by idx_step
            current_blocks.sort(key=lambda row: row[1], reverse=False if (SWITCHER[direction][2] == 1) else True)
            previous_idx = 0
            for block in current_blocks:
                if block[1] == SWITCHER[direction][0]:  # element on boundary
                    setattr(block[0], 'slide_enable', False)
                    setattr(block[0], 'next_'+SWITCHER[direction][3], line_col_idx)
                    setattr(block[0], 'next_'+SWITCHER[direction][4], SWITCHER[direction][0])
                else:  # not boundary element
                    if (block[1] - SWITCHER[direction][2] not in current_blocks[1]) or \
                            (getattr(current_blocks[previous_idx][0], 'slide_enable') is True):
                        setattr(block[0], 'slide_enable', True)
                        setattr(block[0], 'next_'+SWITCHER[direction][3], line_col_idx)
                        # calc next coordinate
                        if previous_idx == 0:
                            setattr(block[0], 'next_' + SWITCHER[direction][4], SWITCHER[direction][0])
                        else:
                            setattr(block[0], 'next_' + SWITCHER[direction][4],
                                    getattr(current_blocks[previous_idx][0],
                                            'next_' + SWITCHER[direction][4]) + SWITCHER[direction][2])
                previous_idx += 1

    def slide_block(self):
        for block in self.blocks:
            if block.slide_enable:
                block.coordinate_x = block.next_coordinate_x
                block.coordinate_y = block.next_coordinate_y
                block.moved = True
                block.slide_enable = False

    def merge_block(self, direction):
        # TODO(Rundong) loop below can be optimised
        for line_col_idx in range(SWITCHER[direction][5]):
            current_blocks = [[block, getattr(block, SWITCHER[direction][4])]
                              for block in self.blocks if getattr(block, SWITCHER[direction][3]) == line_col_idx]
            if len(current_blocks) <= 1:
                continue
            else:
                # merge: (idx_move_start -> idx_boundary] by idx_step
                current_blocks.sort(key=lambda row: row[1], reverse=False if (SWITCHER[direction][2] == -1) else True)
                next_idx = 1
                for block in current_blocks:
                    if next_idx >= len(current_blocks):
                        break
                    else:
                        if getattr(block[0], 'score') == getattr(current_blocks[next_idx][0], 'score'):
                            setattr(current_blocks[next_idx][0], 'score', 2 * getattr(block[0], 'score'))
                            self.blocks.remove(block[0])
                    next_idx += 1

    def generate_block(self):
        self.blocks.append(Block())
        
    def get_max_score(self):
        return max([block.score for block in self.blocks])
