from src.DDPDevice import DDPDevice
from src.utils import load_config

if __name__ == "__main__":
    config = load_config()
    device = DDPDevice(dest_ip=config["dest_ip"])
    device.display_animation(
        dir_path="test_data/badapple_frames",
        fps=30,
        countdown=3,
    )
    device.clear()
