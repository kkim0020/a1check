from __future__ import annotations
from layer_store import SetLayerStore, AdditiveLayerStore, SequenceLayerStore, LayerStore
from layer_util import get_layers
from typing import List
from data_structures.referential_array import ArrayR

class Grid:
    DRAW_STYLE_SET = "SET"
    DRAW_STYLE_ADD = "ADD"
    DRAW_STYLE_SEQUENCE = "SEQUENCE"
    DRAW_STYLE_OPTIONS = (
        DRAW_STYLE_SET,
        DRAW_STYLE_ADD,
        DRAW_STYLE_SEQUENCE
    )

    DEFAULT_BRUSH_SIZE = 2
    MAX_BRUSH = 5
    MIN_BRUSH = 0

    def __init__(self, draw_style, x, y) -> None:
        """
        Initialise the grid object.
        - draw_style:
            The style with which colours will be drawn.
            Should be one of DRAW_STYLE_OPTIONS
            This draw style determines the LayerStore used on each grid square.
        - x, y: The dimensions of the grid.

        Should also intialise the brush size to the DEFAULT provided as a class variable.
        """
        self.draw_style = draw_style
        self.x = x
        self.y = y
        self.brush_size = self.DEFAULT_BRUSH_SIZE

        # initialize gird square each grid have one LayerStore
        self.grid: ArrayR[ArrayR] = ArrayR(x)
        self.set_layer_store()
        self.is_special = False

    def increase_brush_size(self):
        """
        Increases the size of the brush by 1,
        if the brush size is already MAX_BRUSH,
        then do nothing.
        """
        if self.brush_size < self.MAX_BRUSH:
            self.brush_size += 1
        else:
            pass

    def decrease_brush_size(self):
        """
        Decreases the size of the brush by 1,
        if the brush size is already MIN_BRUSH,
        then do nothing.
        """
        if self.brush_size > self.MIN_BRUSH:
            self.brush_size -= 1
        else:
            pass

    def special(self):
        """
        Activate the special affect on all grid squares.
        """

        for i in range(self.x):
            for j in range(self.y):
                pixel: LayerStore = self.grid[i][j]
                pixel.special()
        self.is_special = True

    def __getitem__(self, row_index):
        """
        Get LayerStore of tuple index
        """
        return self.grid[row_index]

    def set_layer_store(self):
        grid_square = ArrayR(self.x)
        for x_ind in range(self.x):
            col = ArrayR(self.y)
            for i in range(self.y):
                if self.draw_style == self.DRAW_STYLE_SET:
                    col[i] = (SetLayerStore())
                elif self.draw_style == self.DRAW_STYLE_ADD:
                    col[i] = (AdditiveLayerStore())
                elif self.draw_style == self.DRAW_STYLE_SEQUENCE:
                    col[i] = (SequenceLayerStore())
                else:
                    raise Exception(f"Draw Style Error {self.draw_style} not exist")
            grid_square[x_ind] = col
        self.grid = grid_square
