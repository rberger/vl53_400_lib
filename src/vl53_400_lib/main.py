#!/usr/bin/env python3
import click
import device_access
from loguru import logger
import sys
import time



class App:
    """
    This class is used to create a CLI application.
    """
    def __init__(self, serial_port: str, baud_rate: int, timeout: int, return_rate: float, debug: bool) -> None:
        """
        This method initializes the class.
        """
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.return_rate = return_rate
        self.debug = debug
        self.device = device_access.Serial(serial_port, baud_rate, timeout)
        
    def stream_data(self) -> None:
        """
        This method streams data from the serial port.
        """
        start_time = time.time()
        count = 0
        while True:
            sample = self.device.get_distance()
            if sample == {} or None:
                logger.warning("No data received. Exiting.")
                break
            else:
                count += 1

                # Calculate rate
                elapsed_time = time.time() - start_time
                rate = count / elapsed_time

                # Print rate
                print(f"Rate: {rate} data points per second")


@click.command()
@click.option("--serial-port", default="/dev/tty.usbserial-910", help="The serial port to connect to.")
@click.option("--baud-rate", default=115200, help="The baud rate to use.")
@click.option("--timeout", default=1, help="The timeout to use.")
@click.option("--return-rate", default=1.0, help="Set Return Rate 0.1 , 0.2 , 0.5 , 1 , 2 , 5 , 10 , 20, 50, 100")
@click.option("--debug", is_flag=True, help="Enable debug logging.")
def main(serial_port: str, baud_rate: int, timeout: int, return_rate: float, debug: bool) -> None:
    logger.info(f"serial_port: {serial_port}, baud_rate: {baud_rate} return_rate: {return_rate} debug: {debug}")
    app = App(serial_port, baud_rate, timeout, return_rate, debug)
    app.stream_data()

if __name__ == "__main__":
    logger.enable("device_access")
    logger.remove(0)
    logger.add(sys.stderr, level="WARNING")
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Closing the serial port.")
        self.ser.close()
