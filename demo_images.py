import time

from src.DDPDevice import DDPDevice
from src.utils import load_config

if __name__ == "__main__":
    config = load_config()
    device = DDPDevice(dest_ip=config["dest_ip"])

    # -------------------------------------------
    print("\nColor image")
    device.display_img("test_data/color.bmp")
    time.sleep(5)

    # -------------------------------------------
    print("\nWide image")
    path = "test_data/heart.bmp"

    print("  - resize")
    device.display_img(path, mode="resize")
    time.sleep(5)

    print("  - pad")
    device.display_img(path, mode="pad")
    time.sleep(5)

    print("  - crop")
    device.display_img(path, mode="crop")
    time.sleep(5)

    # -------------------------------------------
    print("\nTall image")
    path = "test_data/snowman.bmp"

    print("  - resize")
    device.display_img(path, mode="resize")
    time.sleep(5)

    print("  - pad")
    device.display_img(path, mode="pad")
    time.sleep(5)

    print("  - crop")
    device.display_img(path, mode="crop")
    time.sleep(5)

    # -------------------------------------------
    print("\nTiny image")
    path = "test_data/small.bmp"

    print("  - resize")
    device.display_img(path, mode="resize")
    time.sleep(5)

    print("  - pad")
    device.display_img(path, mode="pad")
    time.sleep(5)

    print("  - crop")
    device.display_img(path, mode="crop")
    time.sleep(5)

    # -------------------------------------------
    device.clear()
