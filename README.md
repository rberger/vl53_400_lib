# vl53-400 Library

Python Library and CLI for the VL53-400 laser rangefinder with Serial interface

This is the  [MJ-VL53-400 unit Sold by MengJie](https://www.amazon.com/dp/B0C2YWYW62)

Its basically a [STMicroelectronics VL53L0X](https://www.st.com/en/imaging-and-photonics-solutions/vl53l0x.html). I think its actually a [WitMotion Laser Distance Sensor WT-VL53L0 Distance Module UART Output ](https://witmotion-sensor.com/collections/laser-range-sensor/products/witmotion-laser-distance-sensor-wt-vl53l1-distance-module-uart-output-3-5v) repackaged by MengJie

* [Menjie MJ-VL53-400 User Manual](https://drive.google.com/drive/folders/1UvIrseDLtCvuBqcgA6oYrWwT4huYJUFw)
* [ST API Info](https://www.st.com/en/embedded-software/stsw-img005.html#overview) 

## Library Functions

Class `device_access.SerialAccess` contains all the methods for using it

### Init

``` python
    def __init__(self, serial_port: str, baud_rate: int, timeout: int = 1) -> None:
        """
        This method initializes the class.
        Args:
            serial_port (str): The serial port to connect to.
            baud_rate (int): The baud rate to use.
            timeout (int): The timeout to use.
        """
```

### Reset

``` python
    def reset(self) -> None:
        """
        This method resets the lidar.
        """
```

### Set Sensor mode

``` python
    def set_sensor_mode(self, mode: str) -> None:
        """
        This method sets the sensor mode.
        Args:
            mode (str): The mode to set. (serial, modbus, iic)
                        Probably only want to use serial or modbus. modbus will stop the  serial updates
        """
```

### Get Return Rate

``` python
    def get_return_rate(self) -> str:
        """
        Gets the return rate setting
        Returns:
            str: The return rate in Hz
        """
```

### Set Return Rate

``` python
    def set_return_rate(self, rate: str) -> None:
        """
        Gets the return rate from the lidar
        Returns:
            str: The return rate
        """
```

### Stream Data

Only prints the data to stdout

    ``` python
    def stream_data(self, loop: bool = True) -> None:
        """
        This method streams data from the serial port.
        Args:
            loop (bool): Whether or not to loop forever.
               Defaults to True. Set to false to exit after one loop (for testing)
        """
    ```

### Get Distance

This is the main workhorse function to use

``` python
    def get_distance(self) -> dict[str, str]:
        """
        This method reads data from the serial port and returns a dictionary.
        Returns:
            dict: A dictionary containing the `distance` and `units`,
                  as well as the `state` and `state_code`.
        """
```

## Main.py has a CLI for exercising all functions

## Install and run cli

``` shell
git clone 
cd vl53_400_lib
poetry install
```
### To run the cli:

```
> poetry run vl53 --help

Usage: vl53 [OPTIONS]

Options:
  --serial-port TEXT              The serial port to connect to.
  --baud-rate INTEGER             The baud rate to use.
  --timeout INTEGER               The timeout to use.
  --return-rate [0.1|0.2|0.5|1|2|5|10|20|50|100]
                                  Set Return Rate in Hz
  --mode [serial|modbus|iic]      Comm mode (modbus stops serial spew)
  --op [stream|get_return_rate|lstream|reset]
                                  The operation to perform.
  --debug                         Enable debug logging.
  --help                          Show this message and exit.

```

## TODO:
* Calibration
* Publish to Pypi.org
