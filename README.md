# vl53-400 Laser RangeFinder Library

Python Library and CLI for the VL53-400 laser rangefinder with Serial interface

__NOTE: This is still a bit underconstruction. The Functions here do seem to work, but not all capabilities of the chipset is handled yet. You should be able to do measurements though.__

This is for the  [MJ-VL53-400 unit Sold by MengJie](https://www.amazon.com/dp/B0C2YWYW62).

Its basically a [STMicroelectronics VL53L0X](https://www.st.com/en/imaging-and-photonics-solutions/vl53l0x.html) with a UART so you can use it via a USB -> TTL Serial adapter and not deal with IIC or Modbus.

It seems to actually be a [WitMotion Laser Distance Sensor WT-VL53L0 Distance Module UART Output ](https://witmotion-sensor.com/collections/laser-range-sensor/products/witmotion-laser-distance-sensor-wt-vl53l1-distance-module-uart-output-3-5v) repackaged by MengJie

* [Menjie MJ-VL53-400 User Manual](https://drive.google.com/drive/folders/1UvIrseDLtCvuBqcgA6oYrWwT4huYJUFw)
* [ST API Info](https://www.st.com/en/embedded-software/stsw-img005.html#overview) 

## Library Functions

Class `device_access.SerialAccess` contains all the methods for using it

### Instantiate the RangeFinder Class

``` python
RangeFinder(serial_port: str, baud_rate: int, timeout: int, debug: bool)
```
#### Arguments
Need to supply all of these for now

* `serial_port: str` - The serial port the RangeFinder is connected too such as `/dev/tty.usbserial-910`
* `baud_rate: int` - Baud Rate. Should be `115200`
* `timeout: int` - Timeout. Should use `1`
* `return_rate: float` - Should be one of `"0.1", "0.2", "0.5", "1", "2", "5", "10", "20", "50", "100"`
* `debug: bool` - Set `True` to enable debugging, otherwise `False`

#### Example:

``` python
    from vl53_400_lib import RangeFinder

    range_finder = RangeFinder("/dev/tty.usbserial-910", 115200, 1, 10, False)
```


### Reset

This method resets the Rangefinder.

``` python
    range_finder.reset()
```

### Set Sensor mode

This method sets the sensor mode between serial (default), modbus and iic.

#### Arguments
* `mode: str` - The mode to set. (`serial`, `modbus`, `iic`)
                Probably only want to use serial or modbus.
                modbus will stop the  serial updates

#### Example:

``` python
    range_finder.set_sensor_mode("modbus")

```

### Get Return Rate

Gets the return rate setting

#### Returns

`str`: The return rate in Hz

#### Example

``` python
    rate = range_finder.get_return_rate()
```

### Set Return Rate

#### Arguments

`rate: str` - One of `"0.1", "0.2", "0.5", "1", "2", "5", "10", "20", "50", "100"`

#### Example

``` python
    range_finder.set_return_rate("0.5")
```

### Stream Data

__Only prints the data to stdout__

This method streams data from the serial port to stdout. It does not return
anything and will block until interrupted if loop is True.

#### Argument
`loop: bool` - Whether or not to loop forever.
               Defaults to True.
               Set to false to exit after one loop (for testing)

``` python
range_finder.stream_data(True)
```

### Get Distance

This is the main workhorse function to use. It will fetch the distance data from the Rangefinder
Reads data from the serial port and returns a dictionary.

#### Returns
`data: dict` -  A dictionary containing the `distance` and `units`,
                as well as the `state` and `state_code`.
``` python
    data = range_finder.get_distance()
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
* Make initialization key/values with defaults
* Calibration
