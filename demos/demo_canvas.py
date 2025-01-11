"""
Example showing how to use the Canvas and drawable objects.
"""

import time

from src.DDPDevice import DDPDevice
from src.display import show_image_loop
from src.drawing.canvas import Canvas
from src.drawing.text import Text, TextMarquee
from src.utils import load_config


# Create a DDP device where the canvas will be drawn
config = load_config()
device = DDPDevice(dest_ip=config["dest_ip"])

# Create a canvas object that can hold multiple "drawable" objects
# You can define these objects directly when creating the canvas
canvas = Canvas(
    objects=[
        Text(text="ABCD", font="3x3", x=0, y=0),
        TextMarquee(text="EFGH", font="5x5", y=4, speed=0.5),
    ],
)

# You can also add objects to the canvas after it is created
canvas.add(TextMarquee(text="IJKL", font="5x5", y=10, speed=1.5))

while True:
    # Render out the array (pixels) of the canvas based on its objects
    array = canvas.render()
    # Update the canvas, and all its objects (for example scroll Marquees, etc.)
    canvas.update()
    # Send the pixel array to the device
    device.display_array(data=array)
    # Also show the contents of the pixel array in another window
    show_image_loop(array, scale=50)
    # Sleep by a fraction of the framerate
    time.sleep(1 / 8)
