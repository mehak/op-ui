#!/usr/bin/python
""" Unit tests for op.py, assumes previous run of op """

import unittest
import os
import json
import time
from pathlib import Path
from op import OnePassword


def generate_list_test(objects_name, command):
    """ generator for the list_x tests """
    def method(self):
        op_test = OnePassword()
        op_test.signin()
        objects = getattr(op_test, command)()
        self.assertTrue(len(objects) > 0)

    method.__name__ = objects_name
    return method


class TestInit(unittest.TestCase):
    """ Tests OnePassword methods """
    def setUp(self):
        """ Setup tests """
        self.start_time = time.time()

    def tearDown(self):
        """ Tear down tests and print run time """
        duration = time.time() - self.start_time
        print(f'{self.id()}: {duration}')

    def test_constructor_config_empty(self):
        """ Tests the constructor method with an empty string """
        op_test = OnePassword()
        self.assertEqual(op_test.config_path, str(Path.home()) + '/.op/config')

    def test_constructor_op_string(self):
        """ Tests the constructor method with the path to .op """
        op_test = OnePassword('/home/nmerlin/.op')
        self.assertEqual(op_test.config_path, str(Path.home()) + '/.op/config')

    def test_constructor_config_read(self):
        """ Tests reading the configuration file """
        op_test = OnePassword()
        with open(str(Path.home()) + '/.op/config') as config_file:
            contents = config_file.read()
            self.assertEqual(op_test.config, json.loads(contents))

    def test_signin_all(self):
        """ Tests signing in/reading from the sign-in cache """
        op_test = OnePassword()
        op_test.signin()

        num_sessions = len(op_test.session_tokens)
        num_accounts = len(op_test.config['accounts'])
        self.assertEqual(num_sessions, num_accounts)
        self.assertTrue(os.path.isfile(op_test.session_cache))

    prefix = 'test_list_'
    lis = 'list_'
    test_list_items = generate_list_test(f'{prefix}items', 'list_items')
    test_list_documents = generate_list_test(f'{prefix}documents', 'list_documents')


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestInit)
    unittest.TextTestRunner(verbosity=0).run(SUITE)
