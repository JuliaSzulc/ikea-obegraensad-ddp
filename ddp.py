#import logging
#import logging.handlers
#from ledfx.devices.ddp import DDPDevice

#device = DDPDevice()

import logging
from typing import Union

import struct
import socket

import numpy as np
from numpy import ndarray
from time import sleep


_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.DEBUG)


class DDPDevice:
    """DDP device support"""

    # PORT = 4048
    HEADER_LEN = 0x0A
    # DDP_ID_VIRTUAL     = 1
    # DDP_ID_CONFIG      = 250
    # DDP_ID_STATUS      = 251

    MAX_PIXELS = 480
    MAX_DATALEN = MAX_PIXELS * 3  # fits nicely in an ethernet packet

    VER = 0xC0  # version mask
    VER1 = 0x40  # version=1
    PUSH = 0x01
    QUERY = 0x02
    REPLY = 0x04
    STORAGE = 0x08
    TIME = 0x10
    DATATYPE = 0x01
    SOURCE = 0x01
    TIMEOUT = 1


    def __init__(self, destination, destination_port):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.name = "ddp-device"
        self.destination = destination
        self._device_type = "DDP"
        self.frame_count = 0
        self.connection_warning = False
        self.destination_port = destination_port
    

    def display(self, array: np.ndarray):
        if array.shape != (16, 16):
            raise Exception("Learn to count")

        return self.flush(np.repeat(array.flatten(), 3))


    def flush(self, data: ndarray) -> None:
        """
        Flushes LED data to the DDP device.

        Args:
            data (ndarray): The LED data to be flushed.

        Raises:
            AttributeError: If an attribute error occurs during the flush.
            OSError: If an OS error occurs during the flush.
        """
        self.frame_count += 1
        try:

            DDPDevice.send_out(
                self._sock,
                self.destination,
                self.destination_port,
                data,
                self.frame_count,
            )
            if self.connection_warning:
                # If we have reconnected, log it, come back online, and fire an event to the frontend
                _LOGGER.info(f"DDP connection to {self.name} re-established.")
                self.connection_warning = False
                self._online = True
                #self._ledfx.events.fire_event(DevicesUpdatedEvent(self.id))
        except AttributeError:
            self.activate()
        except OSError as e:
            # print warning only once until it clears
            if not self.connection_warning:
                # If we have lost connection, log it, go offline, and fire an event to the frontend
                _LOGGER.warning(f"Error in DDP connection to {self.name}: {e}")
                self.connection_warning = True
                self._online = False
                #self._ledfx.events.fire_event(DevicesUpdatedEvent(self.id))

    @staticmethod
    def send_out(
        sock: socket, dest: str, port: int, data: ndarray, frame_count: int
    ) -> None:
        """
        Sends out data packets over a socket using the DDP protocol.

        Args:
            sock (socket): The socket to send the packet over.
            dest (str): The destination IP address.
            port (int): The destination port number.
            data (ndarray): The data to be sent in the packet.
            frame_count(int): The count of frames.

        Returns:
        None
        """
        sequence = frame_count % 15 + 1
        byteData = memoryview(data.astype(np.uint8).ravel())
        packets, remainder = divmod(len(byteData), DDPDevice.MAX_DATALEN)
        if remainder == 0:
            packets -= 1  # divmod returns 1 when len(byteData) fits evenly in DDPDevice.MAX_DATALEN

        for i in range(packets + 1):
            data_start = i * DDPDevice.MAX_DATALEN
            data_end = data_start + DDPDevice.MAX_DATALEN
            DDPDevice.send_packet(
                sock,
                dest,
                port,
                sequence,
                i,
                byteData[data_start:data_end],
                i == packets,
            )

    @staticmethod
    def send_packet(
        sock: socket,
        dest: str,
        port: int,
        sequence: int,
        packet_count: int,
        data: Union[bytes, memoryview],
        last: bool,
    ) -> None:
        """
        Sends a DDP packet over a socket to a specified destination.

        Args:
            sock (socket): The socket to send the packet over.
            dest (str): The destination IP address.
            port (int): The destination port number.
            sequence (int): The sequence number of the packet.
            packet_count (int): The total number of packets.
            data (bytes or memoryview): The data to be sent in the packet.
            last (bool): Indicates if this is the last packet in the sequence.

        Returns:
            None
        """
        bytes_length = len(data)
        header = struct.pack(
            "!BBBBLH",
            DDPDevice.VER1 | (DDPDevice.PUSH if last else 0),
            sequence,
            DDPDevice.DATATYPE,
            DDPDevice.SOURCE,
            packet_count * DDPDevice.MAX_DATALEN,
            bytes_length,
        )
        udpData = header + bytes(data)
        
        print(f"Sending {udpData}")
        print(dest)
        print(port)

        sock.sendto(
            udpData,
            (dest, port),
        )


def matrix_to_ddp_data(array: np.ndarray):
    if array.shape != (16, 16):
        raise Exception("Learn to count")
    
    return np.repeat(array.flatten(), 3)



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
device.flush(matrix_to_ddp_data(data))
