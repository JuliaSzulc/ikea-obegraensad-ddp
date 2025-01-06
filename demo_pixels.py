import time

import numpy as np

from src.DDPDevice import DDPDevice
from src.utils import load_config

if __name__ == "__main__":
    config = load_config()
    device = DDPDevice(dest_ip=config["dest_ip"])

    for i in range(16):
        array = np.zeros([16, 16])
        array[:, i] = 50
        device.display_array(array)
        time.sleep(0.2)

    for i in range(16):
        device.display_pixel(i, np.random.randint(0, 16))
        time.sleep(0.2)

    device.clear()
