#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, patch
from vl53_400_lib.device_access import serial, SerialAccess, add_crc, check_crc


class TestSerialAccess(unittest.TestCase):
    @patch("serial.Serial")
    # @patch("vl53_400_lib.device_access.SerialAccess")
    def setUp(self, mock_serial_port):
        self.mock_serial_port = mock_serial_port
        self.serial_port_instance = self.mock_serial_port.return_value
        self.serial_port_obj = serial.Serial("COM1", 9600)

        # self.mock_serial_access = mock_serial_access
        # self.serial_access_instance = self.mock_serial_access.return_value
        self.serial_access_obj = SerialAccess("COM1", 9600)

    def test_reset(self):
        self.serial_access_obj.reset()

        expected_command = add_crc(b"\x50\x06\x00\x00\x00\x01")
        self.serial_port_instance.write.assert_called_once_with(expected_command)
        received_data = bytearray.fromhex("500600000001458b")
        self.serial_port_instance.readline.return_value = received_data
        self.assertTrue(check_crc(received_data))

    def test_send_command(self):
        command = bytearray.fromhex("500600000001")
        self.serial_access_obj.send_command(command)

        serial_port_arg_with_crc = bytearray.fromhex("500600000001458b")
        self.serial_port_instance.write.assert_called_once_with(serial_port_arg_with_crc)

    def test_set_sensor_mode(self):
        self.serial_access_obj.set_sensor_mode("serial")
        expected_command = add_crc(bytearray.fromhex("500600380000"))
        self.serial_port_instance.write.assert_called_once_with(expected_command)

        self.serial_port_instance.reset_mock()
        self.serial_access_obj.set_sensor_mode("modbus")
        expected_command = add_crc(bytearray.fromhex("500600380001"))
        self.serial_port_instance.write.assert_called_once_with(expected_command)

        self.serial_port_instance.reset_mock()
        self.serial_access_obj.set_sensor_mode("iic")
        expected_command = add_crc(bytearray.fromhex("500600380002"))
        self.serial_port_instance.write.assert_called_once_with(expected_command)

    def test_get_return_rate(self):
        self.serial_port_instance.readline.return_value = bytearray.fromhex(
            "5003020009858e53746174653b30202c2052616e67652056616c6964"
        )

        # self.serial_access_obj.get_return_rate()
        result = self.serial_access_obj.get_return_rate()
        print(f"result: {result}")
        self.assertEqual(result, "100")
        expected_command = add_crc(bytearray.fromhex("500300030001"))
        self.serial_port_instance.write.assert_called_once_with(expected_command)

    def test_get_distance(self):
        mock_data = [b"State;4 , Range Valid", b"d: 456 mm"]

        # Simulate multiple readline calls with mock data
        self.serial_port_instance.readline.side_effect = mock_data
        result = self.serial_access_obj.get_distance()
        self.assertEqual(result, {"state_code": "4", "state": "Range Valid", "distance": "456", "units": "mm"})


if __name__ == "__main__":
    unittest.main()
