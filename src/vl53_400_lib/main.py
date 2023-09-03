#!/usr/bin/env python3
import device_access
from loguru import logger


def main() -> None:
    serial_port = "/dev/tty.usbserial-910"
    baud_rate = 115200
    device = device_access.Serial(serial_port, baud_rate)
    sample = device.get_distance()
    print(f"distance: {sample['distance']} {sample['units']}")


if __name__ == "__main__":
    logger.disable("device_access")
    main()
