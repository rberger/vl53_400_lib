#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, patch
from vl53-400-lib import Serial, add_crc, check_crc

class TestSerial(unittest.TestCase):
    @patch('your_module.serial.Serial')
    def setUp(self, mock_serial):
        self.mock_serial = mock_serial
        self.serial_instance = self.mock_serial.return_value
        self.serial_obj = Serial('COM1', 9600)
    
    def test_reset(self):
        self.serial_obj.reset()
        
        expected_command = add_crc(b'\x50\x06\x00\x00\x00\x01')
        self.serial_instance.write.assert_called_once_with(expected_command)
        
        # Simulate receiving data after sending the command
        received_data = b'\x50\x06\x00\x00\x00\x01\x2B\x12'
        self.serial_instance.readline.return_value = received_data
        self.assertTrue(check_crc(received_data))

if __name__ == '__main__':
    unittest.main()
