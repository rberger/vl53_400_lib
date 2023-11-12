import asyncio
import re
from loguru import logger
from modbus_crc import add_crc, check_crc
import serial_asyncio

# Disable logging for this module based on loguru documentation
logger.disable(__name__)


class AsyncSerialAccess:
    """
    This class is used to establish a connection to the serial port and read data from it.
    """

    def __init__(self, serial_port: str, baud_rate: int, timeout: int = 1) -> None:
        """
        This method initializes the class for async usage.
        Args:
            serial_port (str): The serial port to connect to.
            baud_rate (int): The baud rate to use.
            timeout (int): The timeout to use.
        """
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.timeout = timeout

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

    async def open_connection(self):
        self.reader, self.writer = await serial_asyncio.open_serial_connection(
            url=self.serial_port, baudrate=self.baud_rate, timeout=self.timeout
        )

    async def send_command(self, command: bytes) -> None:
        """
        This method sends a command to the serial port. Adds CRC to the command.
        Args:
            command (bytes): The command to send without CRC.
        """
        cmd_with_crc = add_crc(command)
        self.writer.write(cmd_with_crc)
        await self.writer.drain()

    def reset(self) -> None:
        """
        This method resets the lidar.
        """
        self.send_command(b"\x50\x06\x00\x00\x00\x01")

    def set_sensor_mode(self, mode: str) -> None:
        """
        This method sets the sensor mode.
        Args:
            mode (str): The mode to set. (serial, modbus, iic)
                        Probably only want to use serial or modbus. modbus will stop the  serial updates
        """
        if mode == "serial":
            self.send_command(b"\x50\x06\x00\x38\x00\x00")
        elif mode == "modbus":
            self.send_command(b"\x50\x06\x00\x38\x00\x01")
        elif mode == "iic":
            self.send_command(b"\x50\x06\x00\x38\x00\x02")

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

    async def stream_data(self, loop: bool = True) -> None:
        """
        This method streams data from the serial port.
        Args:
            loop (bool): Whether or not to loop forever.
               Defaults to True. Set to false to exit after one loop (for testing)
        """
        while True:
            data = await self.reader.readline()
            print(data.decode("utf-8").strip())
            if not loop:
                break

    async def get_distance(self) -> dict[str, str]:
        """
        This method reads data from the serial port and returns a dictionary.
        Returns:
            dict: A dictionary containing the `distance` and `units`,
                  as well as the `state` and `state_code`.
        """
        try:
            while True:
                try:
                    data = await self.reader.readline()
                    data = data.decode("utf-8").strip()
                except UnicodeDecodeError:
                    logger.warning("UnicodeDecodeError outer read")
                    continue
                state_match = re.match(self.state_regx, data)
                # Check if the data matches the state regex which indicates that the
                # next line of data will contain the distance info
                if state_match:
                    try:
                        next_data = await self.reader.readline()
                        next_data = next_data.decode("utf-8").strip()
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
            self.writer.close()
            await self.writer.wait_closed()
            return {}
        return {}


# Example usage
async def main():
    serial_access = AsyncSerialAccess(serial_port="/dev/tty.usbserial-910", baud_rate=115200)
    await serial_access.open_connection()
    await serial_access.stream_data()


if __name__ == "__main__":
    asyncio.run(main())
