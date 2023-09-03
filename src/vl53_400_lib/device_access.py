#!/usr/bin/env python

import serial
import re
from loguru import logger

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
                data = self.ser.readline().decode("utf-8").strip()
                state_match = re.match(self.state_regx, data)
                # Check if the data matches the state regex which indicates that the
                # next line of data will contain the distance info
                if state_match:
                    next_data = self.ser.readline().decode("utf-8").strip()
                    data_match = re.match(self.data_regx, next_data)
                    assert data_match is not None
                    logger.debug(f"state: {state_match.groupdict()} " f"data = {data_match.groupdict()}")
                    return data_match.groupdict() | state_match.groupdict()

        # To close the serial port gracefully, use Ctrl+C to break the loop
        except KeyboardInterrupt:
            logger.warning("Closing the serial port.")
            self.ser.close()
        return {}
