#!/usr/bin/env python

import serial
import re
from loguru import logger
from modbus_crc import add_crc, check_crc

# Disable logging for this module based on loguru documentation
logger.disable(__name__)


class Serial:
    """
    This class is used to establish a connection to the serial port and read data from it.
    """

    def __init__(self, serial_port: str, baud_rate: int, timeout: int = 1) -> None:
        """
        This method initializes the class.
        Args:
            serial_port (str): The serial port to connect to.
            baud_rate (int): The baud rate to use.
            timeout (int): The timeout to use.
        """
        self.ser = serial.Serial(port=serial_port, baudrate=baud_rate, timeout=1)

        self.state_regx = r"State;(?P<state_code>\d+)\s+,\s+(?P<state>\w+\s+\w+)"
        self.data_regx = r"d:\s+(?P<distance>\d+)\s+(?P<units>\w+)"
        self.rate_lookup = {
            "0.1": "00",
            "0.2": "01",
            "0.5": "02",
            "1": "03",
            "2": "04",
            "5": "05",
            "10": "06",
            "20": "07",
            "50": "08",
            "100": "09",
        }

        self.rate_reverse_lookup = {
            "0x0": "0.1",
            "0x1": "0.2",
            "0x2": "0.5",
            "0x3": "1",
            "0x4": "2",
            "0x5": "5",
            "0x6": "10",
            "0x7": "20",
            "0x8": "50",
            "0x9": "100",
        }

    def send_command(self, command: bytes) -> None:
        """
        This method sends a command to the serial port. Adds CRC to the command.
        Args:
            command (bytes): The command to send without CRC.
        """
        self.ser.write(add_crc(command))

    def reset(self) -> None:
        """
        This method resets the lidar.
        """
        self.send_command(b"\x50\x06\x00\x00\x00\x01")

    def stop(self) -> None:
        """
        This method stops the lidar serial spew.
        """
        self.send_command(b"\x50\x06\x00\x38\x00\x01")

    def get_return_rate(self) -> str:
        """
        Gets the return rate setting
        Returns:
            str: The return rate in Hz
        """
        self.send_command(b"\x50\x03\x00\x03\x00\x01")
        data = self.ser.readline().strip()
        symbolic_rate = self.rate_reverse_lookup[hex(data[4])]
        logger.debug(f"data: {data.hex()} data[4]: {hex(data[4])} symbolic_rate: {symbolic_rate}")
        return symbolic_rate

    def set_return_rate(self, rate: str) -> None:
        """
        Gets the return rate from the lidar
        Returns:
            str: The return rate
        """

        cmd = bytearray(b"\x50\x06\x00\x03\x00") + bytearray.fromhex(self.rate_lookup[rate])
        logger.debug(f"cmd: {cmd.hex()}")
        self.send_command(cmd)

    def stream_data(self) -> None:
        """
        This method streams data from the serial port.
        """
        while True:
            data = self.ser.readline().decode("utf-8").strip()
            print(data)

    def get_distance(self) -> dict[str, str]:
        """
        This method reads data from the serial port and returns a dictionary.
        Returns:
            dict: A dictionary containing the `distance` and `units`,
                  as well as the `state` and `state_code`.
        """
        try:
            while True:
                # Read data from the serial port
                try:
                    data = self.ser.readline().decode("utf-8").strip()
                except UnicodeDecodeError:
                    logger.warning("UnicodeDecodeError outer read")
                    continue
                state_match = re.match(self.state_regx, data)
                # Check if the data matches the state regex which indicates that the
                # next line of data will contain the distance info
                if state_match:
                    try:
                        next_data = self.ser.readline().decode("utf-8").strip()
                    except UnicodeDecodeError:
                        logger.warning("UnicodeDecodeError")
                        continue
                    data_match = re.match(self.data_regx, next_data)
                    assert data_match is not None
                    logger.debug(f"state: {state_match.groupdict()} " f"data = {data_match.groupdict()}")
                    return data_match.groupdict() | state_match.groupdict()

        # To close the serial port gracefully, use Ctrl+C to break the loop
        except KeyboardInterrupt:
            logger.warning("Keyboard Interrupt: Closing the serial port.")
            self.ser.close()
            return {}
        return {}
