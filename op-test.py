#!/usr/bin/python

import unittest
import os
import json
from op import OnePassword
from pathlib import Path


class testInit(unittest.TestCase):
    def test_constructor_config_empty(self):
        op = OnePassword()
        self.assertEqual(op.config_path, str(Path.home()) + '/.op/config')

    def test_constructor_config_string(self):
        op = OnePassword('/home/nmerlin/.op')
        self.assertEqual(op.config_path, str(Path.home()) + '/.op/config')

    def test_constructor_config_read(self):
        op = OnePassword()
        with open(str(Path.home()) + '/.op/config') as f:
            contents = f.read()
            self.assertEqual(op.config, json.loads(contents))

    def test_signin(self):
        op = OnePassword()
        op.sign_in()
        self.assertEqual(len(op.session_tokens), len(op.config['accounts']))
        self.assertTrue(os.path.isfile(op.session_cache))

    def test_list_items(self):
        op = OnePassword()
        op.sign_in()
        items = op.list_items()
        self.assertTrue(len(items) > 0)

if __name__ == '__main__':
    unittest.main()
