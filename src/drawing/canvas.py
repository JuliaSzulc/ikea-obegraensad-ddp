"""
Module containing the Canvas drawing object.
"""

import typing as t

import numpy as np

from src.drawing.common import DrawableObject


class Canvas:
    """
    The class can be seen as a helper wrapper around a numpy array of pixels
    representing an image. Instead of manipulating the pixels of the image
    directly, it instead adds abstraction where entire objects are added to the
    canvas. These can include entire Text objects, or scrolling Text Marquee
    objects.

    Each object might have the functionality to be updated, or perform some
    action that changes how its pixel will be drawn on the canvas. This is
    coordinated by the canvas through a single update call, and the resulting
    image pixels can then be fetched from the Canvas object.

    :param width: The pixel width of the canvas
    :param height: The pixel height of the canvas
    :param objects: Optional initial list of DrawableObject
    """

    def __init__(
        self,
        width: int = 16,
        height: int = 16,
        objects: t.Optional[t.List[DrawableObject]] = None,
    ):
        self.objects = objects or []
        self.width = width
        self.height = height

    def add(self, obj: DrawableObject):
        """
        Add a single DrawableObject to the canvas.
        :param obj: An instance of DrawableObject
        """
        self.objects.append(obj)

    def remove(self, obj: DrawableObject):
        """
        Remove a single DrawableObject to the canvas.
        :param obj: An instance of DrawableObject
        """
        self.objects.remove(obj)

    def update(self):
        """
        Call the update function of DrawableObject in the canvas.
        """
        for obj in self.objects:
            obj.update()

    def render(self) -> np.ndarray:
        """
        Render out the pixels of each DrawableObject on the canvas and return
        the resulting image pixel array.
        :returns: The rendered image array
        """
        canvas = np.zeros((self.width, self.height))

        for obj in self.objects:
            obj.draw(canvas=canvas)

        return canvas
