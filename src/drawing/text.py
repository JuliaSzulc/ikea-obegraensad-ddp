"""
Module containing text drawing functionality.
"""

import typing as t

import cv2
import numpy as np

import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont

from src.drawing.common import DrawableObject, insert


class PixelFontRenderer:
    """
    This class provides functionality to render out text strings using TTF fonts
    as images.
    :param font_file_path: Path to a .ttf font file
    :param font_pixel_width: The width of the resulting text in pixels
    :param font_pixel_height: The height of the resulting text in pixels
    :param font_render_height: Optional different height that the text will be
        rendered with internally, before being scaled to the final
        font_pixel_height. This is useful for some fonts where default size is
        some other than the desired output size.
    """

    def __init__(
        self,
        font_file_path: str,
        font_pixel_width: int,
        font_pixel_height: int,
        font_render_height: t.Optional[int] = None,
    ):
        self.font_pixel_width = font_pixel_width
        self.font_pixel_height = font_pixel_height
        self.font_render_height = font_render_height or font_pixel_height
        self.pillow_font = ImageFont.truetype(
            font=font_file_path,
            size=self.font_render_height,
        )

    def render_text(self, text: str, line_spacing: int = 1) -> np.ndarray:
        """
        Render a text string as an image. The input text can also contain
        newlines or linebreaks and rendered on separate lines.
        :param text: The input text string
        :param line_spacing: Line spacing in pixels if using a multiline string
        :returns: The rendered text image
        """

        lines = text.splitlines()
        num_lines = len(lines)

        if num_lines == 1:
            return self.render_one_line(text=text)

        arrays = [self.render_one_line(text=line) for line in lines]

        summed_line_heights = sum(array.shape[0] for array in arrays)
        max_line_width = max(array.shape[1] for array in arrays)

        new_height = summed_line_heights + line_spacing * (num_lines - 1)

        new_array = np.zeros(shape=(new_height, max_line_width))

        for i, array in enumerate(arrays):
            height, width = array.shape
            y0 = (height + line_spacing) * i
            y1 = y0 + height
            new_array[y0:y1, :width] = array

        return new_array

    def render_one_line(self, text: str) -> np.ndarray:
        """
        Render a single text line as an image.
        :param text: The input text string
        :returns: The rendered text image
        """

        text = text.upper()

        (x0, y0, x1, y1) = self.pillow_font.getbbox(text)

        image_width = x1 - x0
        image_height = y1 - y0

        # Create a blank image
        # See https://pillow.readthedocs.io/en/stable/handbook/concepts.html
        img = Image.new(
            mode="1",
            size=(image_width, image_height * 2),
            color=0,
        )

        # Get a drawing handle
        draw = ImageDraw.Draw(img)

        # Set the font drawing mode to "1" to disable font anti-aliasing
        draw.fontmode = "1"

        # Draw on image
        draw.text(
            xy=(0, 0),
            text=text,
            fill=255,
            font=self.pillow_font,
            # anchor="lt",  # Specify left-top text anchor
            spacing=1,
        )

        # Convert PIL Image to Numpy array for processing
        array = np.array(img) * np.uint8(255)
        # print(array[:20, :20])
        # array = np.max(array, axis=2)

        if array.max() == 0:
            return np.zeros(shape=(self.font_pixel_height, 1))

        # https://stackoverflow.com/questions/55917328/numpy-trim-zeros-in-2d-or-3d
        nz = np.nonzero(array)  # Indices of all nonzero elements

        start_row = nz[0].min()
        end_row = nz[0].max() + 1

        start_col = nz[1].min()
        end_col = nz[1].max() + 1

        arr_trimmed = array[start_row:end_row, start_col:end_col]

        current_width = arr_trimmed.shape[1]
        current_height = arr_trimmed.shape[0]

        final_height = self.font_pixel_height
        final_width = int(final_height / current_height * current_width)

        result = cv2.resize(
            arr_trimmed,
            (final_width, final_height),
            interpolation=cv2.INTER_AREA,
        )

        return result


# Hard-coded font definitions
FONTS = {
    "3x3": PixelFontRenderer(
        font_file_path="fonts/3x3-Mono.ttf",
        font_pixel_width=3,
        font_pixel_height=3,
        font_render_height=8,
    ),
    "3x5": PixelFontRenderer(
        font_file_path="fonts/3x5 MT Pixel.ttf",
        font_pixel_width=3,
        font_pixel_height=5,
    ),
    "5x5": PixelFontRenderer(
        font_file_path="fonts/5x5 MT Pixel.ttf",
        font_pixel_width=5,
        font_pixel_height=5,
    ),
    "5x7": PixelFontRenderer(
        font_file_path="fonts/5x7 MT Pixel.ttf",
        font_pixel_width=5,
        font_pixel_height=7,
    ),
}


def get_pixel_font_renderer_by_name(font: str) -> PixelFontRenderer:
    """
    Get an instance of a PixelFontRenderer based on a name.
    :param font: The name of the desired font
    :returns: An instance of a PixelFontRenderer
    """
    if font not in FONTS:
        raise ValueError(f"Unknown font {font}, expected one of {list(FONTS.keys())}")
    return FONTS[font]


class Text(DrawableObject):
    """
    A simple static text object.
    :param text: The text string to display
    :param font: The name of the font to be used
    :param x: The top left x position of the text
    :param y: The top left y position of the text
    """

    def __init__(
        self,
        text: str,
        font: str,
        x: int,
        y: int,
    ):
        self.x = x
        self.y = y
        self.text = text
        self.font_renderer = get_pixel_font_renderer_by_name(font=font)
        self.text_array = self.font_renderer.render_text(text=self.text)

    def draw(self, canvas: np.ndarray):
        insert(
            base=canvas,
            array=self.text_array,
            x=self.x,
            y=self.y,
            inplace=True,
        )


class TextMarquee(Text):
    """
    A scrolling text object.
    :param text: The text string to display
    :param font: The name of the font to be used
    :param y: The top left y position of the text
    :param x: The top left x position of the text
    :param speed: The speed of the marquee scrolling effect
    :param screen_width: The width of the screen to be scrolled
    """

    def __init__(
        self,
        text: str,
        font: str,
        y: int,
        x: int = 0,
        speed: float = 1.0,
        screen_width: int = 16,
    ):
        super().__init__(text=text, font=font, x=x, y=y)
        self.speed = speed
        self.screen_width = screen_width
        self.text_width = self.text_array.shape[1]
        self.scroll_distance_x = max(self.screen_width, self.text_width)

    def update(self):
        self.x -= self.speed
        if self.x < -self.scroll_distance_x:
            self.x = self.screen_width
