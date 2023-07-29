#!/usr/bin/env python3
"""Unit test script for myenergi client.
"""

import unittest
import myenergi
# from myenergi.api import API
# from myenergi.error import ParameterError


class TestAPIInitialization(unittest.TestCase):

    def test_valid_initialization(self):
        # Test valid initialization with correct serial number and password
        serial = "10657391"  # Replace with a valid serial number
        password = "myestsg015A"  # Replace with a valid password
        with myenergi.API(serial, password) as api:
            self.assertIsInstance(api, myenergi.API)
            self.assertIsNotNone(api._url)  # Check if the API URL is properly set
            self.assertIsNotNone(api._devices)  # Check if the devices dictionary is initialized
            self.assertIsInstance(api._devices, myenergi.const.devices)

    def test_invalid_initialization_missing_credentials(self):
        # Test initialization with missing serial number and password
        with self.assertRaises(AssertionError):
            with myenergi.API() as api:
                pass

    def test_invalid_initialization_missing_serial_number(self):
        # Test initialization with missing serial number
        password = "myestsg015A"  # Replace with a valid password
        with self.assertRaises(AssertionError):
            with myenergi.API(password=password) as api:
                pass

    def test_invalid_initialization_missing_password(self):
        # Test initialization with missing password
        serial = "10657391"  # Replace with a valid serial number
        with self.assertRaises(AssertionError):
            with myenergi.API(serial=serial) as api:
                pass

    def test_invalid_initialization_invalid_serial_number(self):
        # Test initialization with an invalid serial number
        serial = "123456789"  # Replace with an invalid serial number
        password = "myestsg015A"  # Replace with a valid password
        with self.assertRaises(SystemExit):
            with myenergi.API(serial=serial, password=password) as api:
                pass

    def test_invalid_initialization_invalid_password(self):
        # Test initialization with an invalid password
        serial = "10657391"   # Replace with a valid serial number
        password = "not_a_password"  # Replace with an invalid password
        with self.assertRaises(SystemExit):
            with myenergi.API(serial=serial, password=password) as api:
                pass


if __name__ == "__main__":
    unittest.main()
