import numpy as np

from ddp import DDPDevice


device = DDPDevice(destination="192.168.100.101", destination_port=4048)

# data_1 = np.zeros(3*256)
# #data_2 = np.full(17, fill_value=20)
# data_2 = np.zeros(3*256)
# data_2[:6] = 255

# device.flush(data=data_1)
# # sleep(1)
# device.flush(data=data_2)

# while True:
#     device.flush(np.zeros(3*256))
#     for i in range(3, 256 * 3 + 1, 3):
#         data = np.zeros(3*256)
#         data[:i] = 255
#         device.flush(data=data)
#         sleep(0.2)

data = np.zeros([16, 16])

# for i in range(16):
#     data[i] = 16 * i + 1

device.display(data)
