"""
Example showing how pixel fonts are rendered as image.
"""

from src.drawing.text import FONTS

from src.display import show_images_static


def main():

    # Define some example input text
    text = "the quick, brown fox jumps over the lazy dog: 1234567890"
    # Define another example text that is also multiline
    text_multiline = text + "\nHello World!"

    # Render out the texts as numpy arrays using the fonts
    array_3x3 = FONTS["3x3"].render_text(text=text)
    array_3x5 = FONTS["3x5"].render_text(text=text)
    array_5x5 = FONTS["5x5"].render_text(text=text)
    array_5x7 = FONTS["5x7"].render_text(text=text)
    array_5x7_multiline = FONTS["5x7"].render_text(text=text_multiline)

    # Show the results in separate windows
    show_images_static(
        images=[
            array_3x3,
            array_3x5,
            array_5x5,
            array_5x7,
            array_5x7_multiline,
        ],
        scale=5,
    )


if __name__ == "__main__":
    main()
