#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, patch
from vl53-400-lib import Serial

class TestSerial(unittest.TestCase):
    @patch('your_module.serial.Serial')
    def setUp(self, mock_serial):
        self.mock_serial = mock_serial
        self.serial_instance = self.mock_serial.return_value
        self.serial_obj = Serial('COM1', 9600)
    
    def test_get_distance(self):
        mock_data = [
            b'State;123 , Normal',
            b'd: 456 meters',
            b'Other data',
        ]
        
        # Simulate multiple readline calls with mock data
        self.serial_instance.readline.side_effect = mock_data
        result = self.serial_obj.get_distance()
        
        self.assertEqual(result, {'state_code': '123', 'state': 'Normal', 'distance': '456', 'units': 'meters'})
        expected_calls = [call().decode('utf-8') for call in self.serial_instance.readline.call_list()]
        self.assertEqual(expected_calls, [mock_data[0], mock_data[1]])
        
if __name__ == '__main__':
    unittest.main()
