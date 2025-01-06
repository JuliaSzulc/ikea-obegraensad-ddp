import glob
import logging
import time
from pathlib import Path
from typing import Literal

import numpy as np
from PIL import Image

from src.DDPAgent import _DDPAgent

logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")
_LOGGER = logging.getLogger(__file__)
_LOGGER.setLevel(logging.DEBUG)


class DDPDevice:
    def __init__(
        self,
        dest_ip: str,
        resolution: tuple[int, int] = (16, 16),
        dest_port: int = 4048,
        name: str = "ddp-obegransead",
    ):
        self.resolution = resolution
        self.name = name

        self._agent = _DDPAgent(
            dest_ip=dest_ip,
            dest_port=dest_port,
            resolution=self.resolution,
            name=self.name,
        )

    def display_array(self, data: np.ndarray) -> None:
        """
        Displays the data given as a pixel array.
        Values can be either integers [0-255] - indicating brightness, or booleans -
        ignoring brightness setting.

        Args:
            data: Array of LED brightness values.

        Raises:
            ValueError: If shape of the data is different from the LED array dimensions.
        """
        if data.shape != self.resolution:
            msg = (
                f"Incorrect dimensions of the input data - {data.shape}. ",
                f"Must be {self.resolution}."
            )
            raise ValueError(msg)

        if data.dtype == bool:
            data = data.astype(int) * 255
        elif np.any((data < 0) | (data > 255)):
            _LOGGER.warning("Values outside allowed range. Clipping to [0-255].")
            data = data.clip(0, 255)

        # each value needs to be repeated 3 times for RGB value format
        data = np.repeat(data.flatten(), 3)

        self._agent.flush(data)

    def display_pixel(self, x: int, y: int, value: int = 255) -> None:
        """
        Lights up a single pixel.

        Args:
            x: Row of the LED.
            y: column of the LED.
            value: Brightness of the pixel. Defaults to 255.

        Raises:
            ValueError: If coordinates are out of bounds of the defined resolution.
        """
        if x not in range(self.resolution[0]) or y not in range(self.resolution[1]):
            msg = f"Coordinates ({x}, {y}) out of bounds {self.resolution}."
            raise ValueError(msg)

        data = np.zeros(self.resolution)
        data[x, y] = value
        self.display_array(data)

    def clear(self) -> None:
        """
        Turns off all the LEDs.
        """
        self.display_array(np.zeros(self.resolution))

    def display_img(
        self,
        path: Path | str,
        mode: Literal["resize", "crop", "pad"] = "resize",
    ) -> None:
        """
        Loads and displays an image file.
        Image is first converted to grayscale. Then, if its size is not exactly the same
        as the resolution, it can be cropped (from top left corner), resized or padded
        (if the image is larger it's first resized and then padded).

        Args:
            path: Path to the image file.
            mode: Preprocessing option of images with different resolution. Defaults to
                "resize".

        Raises:
            FileExistsError: If the path does not point to a file.
            ValueError: If unsupported `mode` value is passed.
        """
        path = Path(path)
        if not path.exists() or not path.is_file():
            raise FileExistsError(f"File `{path}` does not exist.")

        img = Image.open(path).convert("L")  # convert to 8-bit grayscale
        if img.size != self.resolution:
            x, y = img.size
            match mode:
                case "resize":
                    img = img.resize(self.resolution)
                case "crop":
                    img = img.crop([0, 0, self.resolution[0], self.resolution[1]])
                case "pad":
                    bound = max(x, y, *self.resolution)
                    padded_img = Image.new("L", (bound, bound), "black")
                    padded_img.paste(img, (int((bound - x) / 2), int((bound - y) / 2)))
                    img = padded_img.resize(self.resolution)
                case _:
                    raise ValueError(f"Incorrect `mode` given ({mode}).")
        self.display_array(np.array(img))

    def display_animation(
        self,
        dir_path: Path | str,
        fps: int = 30,
        countdown: int = 0,
    ) -> None:
        dir_path = Path(dir_path)
        if not dir_path.exists() or not dir_path.is_dir():
            raise FileExistsError(f"Directory `{dir_path}` does not exist.")

        imgs = [
            np.array(Image.open(filepath).convert("L"))
            for filepath
            in glob.glob(f"{dir_path}/**/*.bmp")
        ]
        _LOGGER.debug(f"{len(imgs)} frames found in `{dir_path}`.")

        for i in reversed(range(countdown + 1)):
            time.sleep(1)
            print(f"{i}...")

        start_time = time.time()
        for i, img in enumerate(imgs):
            self.display_array(img)
            _LOGGER.debug(f"Frame {i}/{len(imgs)}")
            expected_elapsed = start_time + (i + 1) * (1 / fps)
            time.sleep(expected_elapsed - time.time())
