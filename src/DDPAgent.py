import logging
import socket
import struct
from typing import Union

import numpy as np

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.DEBUG)


class _DDPAgent():
    """
    DDP interface. Implements direct communication with the device using DDP protocol.
    Mostly copied from https://github.com/LedFx/LedFx
    """
    _HEADER_LEN = 0x0A

    _MAX_PIXELS = 480
    _MAX_DATALEN = _MAX_PIXELS * 3  # fits nicely in an ethernet packet

    _VER = 0xC0  # version mask
    _VER1 = 0x40  # version=1
    _PUSH = 0x01
    _QUERY = 0x02
    _REPLY = 0x04
    _STORAGE = 0x08
    _TIME = 0x10
    _DATATYPE = 0x01
    _SOURCE = 0x01
    _TIMEOUT = 1

    def __init__(
        self,
        dest_ip: str,
        resolution: tuple[int, int],
        dest_port: int = 4048,
        name: str = "ddp-device",
    ) -> None:
        """
        Args:
            dest_ip: IP address of the DDP device
            dest_port: Port of the DDP device. Defaults to 4048.
            resolution: Number of LED rows and columns.
            name: Identifier of the device. Defaults to "ddp-device".
        """
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.resolution = resolution
        self.name = name

        self._sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._frame_count = 0
        self._connection_warning = False

    @staticmethod
    def send_out_packets(
        sock: socket.socket,
        dest_ip: str,
        port: int,
        data: np.ndarray,
        frame_count: int,
    ) -> None:
        """
        Sends out data packets over a socket using the DDP protocol.

        Args:
            sock: The socket to send the packet over.
            dest: The destination IP address.
            port: The destination port number.
            data: The data to be sent in the packet.
            frame_count: The count of frames.
        """
        sequence = frame_count % 15 + 1
        byteData = memoryview(data.astype(np.uint8).ravel())
        packets, remainder = divmod(len(byteData), _DDPAgent._MAX_DATALEN)
        if remainder == 0:
            # divmod returns 1 when len(byteData) fits evenly in _MAX_DATALEN
            packets -= 1

        for i in range(packets + 1):
            data_start = i * _DDPAgent._MAX_DATALEN
            data_end = data_start + _DDPAgent._MAX_DATALEN
            _DDPAgent.send_packet(
                sock,
                dest_ip,
                port,
                sequence,
                i,
                byteData[data_start:data_end],
                i == packets,
            )

    @staticmethod
    def send_packet(
        sock: socket.socket,
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
            sock: The socket to send the packet over.
            dest: The destination IP address.
            port: The destination port number.
            sequence: The sequence number of the packet.
            packet_count: The total number of packets.
            data: The data to be sent in the packet.
            last: Indicates if this is the last packet in the sequence.
        """
        bytes_length = len(data)
        header = struct.pack(
            "!BBBBLH",
            _DDPAgent._VER1 | (_DDPAgent._PUSH if last else 0),
            sequence,
            _DDPAgent._DATATYPE,
            _DDPAgent._SOURCE,
            packet_count * _DDPAgent._MAX_DATALEN,
            bytes_length,
        )
        udpData = header + bytes(data)

        sock.sendto(udpData, (dest, port))

    def flush(self, data: np.ndarray) -> None:
        """
        Flushes LED data to the DDP device.

        Args:
            data: The LED data to be flushed.

        Raises:
            OSError: If an OS error occurs during the flush.
        """
        self._frame_count += 1
        try:

            _DDPAgent.send_out_packets(
                self._sock,
                self.dest_ip,
                self.dest_port,
                data,
                self._frame_count,
            )
            if self._connection_warning:
                # If we have reconnected, log it, come back online, and fire an event to
                # the frontend
                _LOGGER.info(f"DDP connection to {self.name} re-established.")
                self._connection_warning = False
        except OSError as e:
            # print warning only once until it clears
            if not self._connection_warning:
                # If we have lost connection, log it, go offline, and fire an event to
                # the frontend
                _LOGGER.warning(f"Error in DDP connection to {self.name}: {e}")
                self._connection_warning = True
