#!/usr/bin/python
""" op.py - cli wrapper around op """

import json
import os
from pathlib import Path
from subprocess import run

class OnePassword:
    """ Class responsible for wrapping op """
    def __init__(self, op_path=None):
        self.command = '/usr/bin/op'

        if op_path:
            self.op_path = op_path
        else:
            home = str(Path.home())
            self.op_path = home + '/.op'

        self.config_path = self.op_path + '/config'
        self.session_cache = self.op_path + '/session_cache'

        with open(self.config_path) as config_file:
            self.config = json.loads(config_file.read())

        self.session_tokens = []

    def sign_in(self, use_cache=True):
        """ Either read from a cache or sign-in to all accounts """
        if use_cache and os.path.isfile(self.session_cache):
            with open(self.session_cache) as session_file:
                self.session_tokens = json.loads(session_file.read())

                for token in self.session_tokens:
                    os.environ['OP_SESSION_' + token['subdomain']] = token['token']
        else:
            for account in self.config['accounts']:
                subdomain = account['shorthand']
                command = [self.command, 'signin', subdomain, '--output=raw']
                output = run(command, capture_output=True)
                token = output.stdout.decode('utf8').rstrip('\n')
                session_token = {'subdomain': subdomain, 'token': token}

                self.session_tokens.append(session_token)

            with open(self.session_cache, 'w') as session_file:
                session_file.write(json.dumps(self.session_tokens))

    def list_items(self):
        """ Get a list of items from all accounts """
        items = []
        for token in self.session_tokens:
            command = [self.command, 'list', 'items', '--account=' + token['subdomain']]
            output = run(command, capture_output=True)
            items_subdomain = json.loads(output.stdout.decode('utf8'))
            items += items_subdomain

        return items
