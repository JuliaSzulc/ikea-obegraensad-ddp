"""
Module containing common drawing functionality.
"""

import numpy as np


class DrawableObject:
    """
    This class is an abstraction of a drawable object. It exists only to
    provide a common shared base for all drawable objects for the Canvas.
    """

    def update(self):
        """
        Method used to update the object and change its values in some way.
        """
        pass

    def draw(self, canvas: np.ndarray):
        """
        Method used to draw the object on the given canvas.
        NOTE: This will modify the input canvas in-place.
        :param canvas: A numpy array representing the image canvas
        """
        pass


def insert(
    base: np.ndarray,
    array: np.ndarray,
    x: float,
    y: float,
    inplace: bool = True,
) -> np.ndarray:
    """
    Insert one numpy array into a base array, overlapping them.
    :param base: The base numpy array
    :param array: The array to be inserted/overlapped
    :param x: The x offset where the array will be inserted
    :param y: The y offset where the array will be inserted
    :param inplace: Modify the base array in-place, otherwise return a new copy
    :returns: The modified base array
    """

    x = round(x)
    y = round(y)

    if not inplace:
        base = base.copy()

    # Determine what parts of the actual array are overlapping with the base

    base_rows, base_cols = base.shape
    array_rows, array_cols = array.shape

    if x >= 0:

        # If the array is completely to the right of the base, return
        if x >= base_cols:
            return base

        base_start_col = x
        base_end_col = min(x + array_cols, base_cols)

        array_start_col = 0
        array_end_col = min(
            array_start_col + (base_end_col - base_start_col), array_cols
        )

    elif x < 0:

        # If the array is completely to the left of the base, return
        if x + array_cols <= 0:
            return base

        base_start_col = 0
        base_end_col = min(x + array_cols, base_cols)

        array_start_col = -x
        array_end_col = min(
            array_start_col + (base_end_col - base_start_col), array_cols
        )

    if y >= 0:

        # If the array is completely to the bottom of the base, return
        if y >= base_rows:
            return base

        base_start_row = y
        base_end_row = min(y + array_rows, base_rows)

        array_start_row = 0
        array_end_row = min(
            array_start_row + (base_end_row - base_start_row), array_rows
        )

    elif y < 0:

        # If the array is completely to the top of the base, return
        if y + array_rows <= 0:
            return base

        base_start_row = 0
        base_end_row = min(y + array_rows, base_rows)

        array_start_row = -y
        array_end_row = min(
            array_start_row + (base_end_row - base_start_row), array_rows
        )

    array_overlap = array[array_start_row:array_end_row, array_start_col:array_end_col]

    base[base_start_row:base_end_row, base_start_col:base_end_col] = array_overlap

    return base
