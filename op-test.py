#!/usr/bin/python

import unittest
from op import OnePassword
import json
from pathlib import Path


class testInit(unittest.TestCase):
    def test_constructor_config_empty(self):
        op = OnePassword()
        self.assertEqual(op.config_path, str(Path.home()) + '/.op/config')

    def test_constructor_config_string(self):
        op = OnePassword('/home/nmerlin/.op/config')
        self.assertEqual(op.config_path, str(Path.home()) + '/.op/config')

    def test_constructor_config_read(self):
        op = OnePassword()
        with open(str(Path.home()) + '/.op/config') as f:
            contents = f.read()
            self.assertEqual(op.config, json.loads(contents))


if __name__ == '__main__':
    unittest.main()
