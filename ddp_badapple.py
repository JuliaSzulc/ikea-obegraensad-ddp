import glob
import time

from PIL import Image
import numpy as np

from ddp import DDPDevice

device = DDPDevice(destination="192.168.100.101", destination_port=4048)

dirpath = "badapple_frames/"
framerate = 1 / 30

imgs = [
    np.array(Image.open(filepath))[:, :, 0]
    for filepath
    in glob.glob(f"{dirpath}**/*.bmp")
]

for i in range(5):
    time.sleep(1)
    print(f"{4-i}\n")

start_time = time.time()
for i, img in enumerate(imgs):
    device.display(img)

    expected_elapsed = start_time + (i + 1) * framerate
    elapsed = time.time() - start_time

    time.sleep(expected_elapsed - time.time())
