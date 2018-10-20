#!/usr/bin/python
""" Unit tests for op.py, assumes previous run of op """

import unittest
import os
import json
import time
from pathlib import Path
from op import OnePassword


class TestInit(unittest.TestCase):
    """ Tests OnePassword methods """
    def setUp(self):
        """ Setup tests """
        self.startTime = time.time()

    def tearDown(self):
        """ Tear down tests and print run time """
        duration = time.time() - self.startTime
        print(f'{self.id()}: {duration}')

    def test_constructor_config_empty(self):
        """ Tests the constructor method with an empty string """
        op = OnePassword()
        self.assertEqual(op.config_path, str(Path.home()) + '/.op/config')

    def test_constructor_op_string(self):
        """ Tests the constructor method with the path to .op """
        op = OnePassword('/home/nmerlin/.op')
        self.assertEqual(op.config_path, str(Path.home()) + '/.op/config')

    def test_constructor_config_read(self):
        """ Tests reading the configuration file """
        op = OnePassword()
        with open(str(Path.home()) + '/.op/config') as config_file:
            contents = config_file.read()
            self.assertEqual(op.config, json.loads(contents))

    def test_signin_all(self):
        """ Tests signing in/reading from the sign-in cache """
        op = OnePassword()
        op.signin()
        self.assertEqual(len(op.session_tokens), len(op.config['accounts']))
        self.assertTrue(os.path.isfile(op.session_cache))

    def test_list_items(self):
        """ Tests the wrapper around op list items """
        op = OnePassword()
        op.signin()
        items = op.list_items()
        self.assertTrue(len(items) > 0)

    def test_list_documents(self):
        """ Tests the wrapper around op list documents """
        op = OnePassword()
        op.signin()
        documents = op.list_documents()
        self.assertTrue(len(documents) > 0)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInit)
    unittest.TextTestRunner(verbosity=0).run(suite)
