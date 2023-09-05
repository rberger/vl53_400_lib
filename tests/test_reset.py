#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, patch
from vl53_400_lib.device_access import serial, add_crc, check_crc, SerialAccess


class TestSerial(unittest.TestCase):
    @patch("serial.Serial")
    @patch("vl53_400_lib.device_access.SerialAccess")
    def setUp(self, mock_serial_access, mock_serial):
        self.mock_serial = mock_serial
        self.serial_instance = self.mock_serial.return_value
        self.serial_obj = serial.Serial("COM1", 9600)

        self.mock_serial_access = mock_serial_access
        self.serial_access_instance = self.mock_serial_access.return_value
        self.serial_access_obj = SerialAccess("COM1", 9600)

    def test_reset(self):
        self.serial_access_obj.reset()

        expected_command = add_crc(b"\x50\x06\x00\x00\x00\x01")
        self.serial_instance.write.assert_called_once_with(expected_command)
        received_data = bytearray.fromhex("500600000001458b")
        self.serial_instance.readline.return_value = received_data
        self.assertTrue(check_crc(received_data))


if __name__ == "__main__":
    unittest.main()
