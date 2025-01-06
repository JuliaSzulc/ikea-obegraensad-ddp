"""
Utility functions used to visualize images by displaying them in windows.
"""

import typing as t

import cv2
import numpy as np


def scale_image(image: np.ndarray, scale: float) -> np.ndarray:
    """
    Scale an image using nearest-neighbor interpolation (good for pixel art).
    :param image: The input image represented as a numpy array
    :param scale: Scale multiplier that will be applied to the image
    :returns: The resulting scaled image
    """
    return cv2.resize(
        image,
        (image.shape[1] * scale, image.shape[0] * scale),
        interpolation=cv2.INTER_NEAREST,
    )


def show_image_loop(image: np.ndarray, scale: t.Optional[float] = None):
    """
    Show an image in a separate window. This function can be called from within
    a loop to show an animation when the image changes every iteration.
    :param image: The input image represented as a numpy array
    :param scale: Scale multiplier that will be applied to the image
    """

    if scale is not None:
        image = scale_image(image=image, scale=scale)

    cv2.imshow("Image", image)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        return


def show_image_static(image: np.ndarray, scale: t.Optional[float] = None):
    """
    Show an image in a separate window.
    :param image: The input image represented as a numpy array
    :param scale: Scale multiplier that will be applied to the image
    """

    if scale is not None:
        image = scale_image(image=image, scale=scale)

    cv2.imshow("Image", image)

    if cv2.waitKey(0) & 0xFF == ord("q"):
        return


def show_images_static(images: t.List[np.ndarray], scale: t.Optional[float] = None):
    """
    Show several images, each in separate windows.
    :param image: The input image represented as a numpy array
    :param scale: Scale multiplier that will be applied to all images
    """

    if scale is not None:
        images = [scale_image(image=image, scale=scale) for image in images]

    for i, image in enumerate(images, start=1):
        cv2.imshow(f"Image {i}", image)

    if cv2.waitKey(0) & 0xFF == ord("q"):
        return
