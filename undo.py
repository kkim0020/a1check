from __future__ import annotations
from action import PaintAction
from grid import Grid
from data_structures.stack_adt import ArrayStack

class UndoTracker:
    def __init__(self):
        self.array_stack : ArrayStack = ArrayStack(10000)
    def add_action(self, action: PaintAction) -> None:
        """
        Adds an action to the undo tracker.

        If your collection is already full,
        feel free to exit early and not add the action.
        """
        for i in range(self.array_stack.length, len(self.array_stack.array)):
            if i is None:
                break
            else:
                self.array_stack.array[i] = None
        # push action
        self.array_stack.push(action)

    def undo(self, grid: Grid) -> PaintAction|None:
        """
        Undo an operation, and apply the relevant action to the grid.
        If there are no actions to undo, simply do nothing.

        :return: The action that was undone, or None.
        """
        try:
            undoing_action: PaintAction = self.array_stack.pop()
            undoing_action.undo_apply(grid)
            return undoing_action

        except:
            return None

    def redo(self, grid: Grid) -> PaintAction|None:
        """
        Redo an operation that was previously undone.
        If there are no actions to redo, simply do nothing.

        :return: The action that was redone, or None.
        """
        if self.array_stack.array[self.array_stack.length] is None:
            return None
        try:
            self.array_stack.length += 1
            redoing_action: PaintAction = self.array_stack.peek()
            redoing_action.redo_apply(grid)
            return redoing_action
        except:
            return None