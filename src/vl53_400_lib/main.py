#!/usr/bin/env python3
import click
from .device_access import SerialAccess
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
        self.device = SerialAccess(serial_port, baud_rate, timeout)
        self.count = 0
        self.start_time = time.time()

    def reset(self) -> None:
        self.device.reset()

    def set_sensor_mode(self, mode) -> None:
        self.device.set_sensor_mode(mode)

    def lstream_data(self) -> None:
        self.device.stream_data()

    def calc_rate(self) -> int:
        """
        This method calculates the rate at which data is received from the lidar.
        """
        self.count += 1

        # Calculate rate
        elapsed_time = time.time() - self.start_time
        rate = self.count / elapsed_time

        logger.debug(f"Rate: {rate} data points per second")
        return rate

    def stream_data(self) -> None:
        """
        This method streams data from the serial port.
        """
        self.start_time = time.time()
        self.count = 0
        while True:
            sample = self.device.get_distance()
            if sample == {} or None:
                logger.warning("No data received. Exiting.")
                break
            else:
                print(f"{sample['distance']} {sample['units']}\t{sample['state']}")

    def get_return_rate(self) -> str:
        """
        Gets the return rate from the lidar
        Returns:
            str: The return rate
        """
        result = self.device.get_return_rate()
        click.echo(f"Return Rate: {result}Hz")
        return result

    def set_return_rate(self, rate) -> None:
        """
        Sets the return rate from the lidar
        Returns:
            str: The return rate
        """
        self.device.set_return_rate(rate)


def exit_with_msg(msg):
    ctx = click.get_current_context()
    click.echo(f"Error: {msg}", err=True)
    click.echo(main.get_help(ctx))


@click.command()
@click.option("--serial-port", default="/dev/tty.usbserial-910", help="The serial port to connect to.")
@click.option("--baud-rate", default=115200, help="The baud rate to use.")
@click.option("--timeout", default=1, help="The timeout to use.")
@click.option(
    "--return-rate",
    type=click.Choice(["0.1", "0.2", "0.5", "1", "2", "5", "10", "20", "50", "100"]),
    help="Set Return Rate in Hz",
)
@click.option("--mode", type=click.Choice(["serial", "modbus", "iic"]), help="Comm mode (modbus stops serial spew)")
@click.option(
    "--op", type=click.Choice(["stream", "get_return_rate", "lstream", "reset"]), help="The operation to perform."
)
@click.option("--debug", is_flag=True, help="Enable debug logging.")
def cli(serial_port: str, baud_rate: int, timeout: int, return_rate: float, mode: str, op: str, debug: bool) -> None:
    logger.enable("device_access")
    logger.remove(0)
    if debug:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="WARNING")
    logger.info(f"serial_port: {serial_port}, baud_rate: {baud_rate} return_rate: {return_rate} debug: {debug}")
    app = App(serial_port, baud_rate, timeout, return_rate, debug)

    op = "set_return_rate" if return_rate else op
    op = "mode" if mode else op
    match op:
        case "reset":
            app.reset()
        case "mode":
            app.set_sensor_mode("mode")
        case "get_return_rate":
            result = app.get_return_rate()
        case "stream":
            app.stream_data()
        case "lstream":
            app.lstream_data()
        case "set_return_rate":
            app.set_return_rate(return_rate)
        case _:
            exit_with_msg("No operation specified. Exiting.")


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        logger.warning("Closing the serial port.")
        self.ser.close()
