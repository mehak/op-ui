#!/usr/bin/python

import json
import os
from pathlib import Path
from subprocess import run

class OnePassword:
    def __init__(self, op_path=None):
        self.command = '/usr/bin/op'

        if (op_path):
            self.op_path = op_path
        else:
            home = str(Path.home())
            self.op_path = home + '/.op'

        self.config_path = self.op_path + '/config'
        self.session_cache = self.op_path + '/session_cache'

        with open(self.config_path) as f:
            self.config = json.loads(f.read())

        self.session_tokens = []

    def sign_in(self, use_cache=True):
        if use_cache and os.path.isfile(self.session_cache):
            with open(self.session_cache) as f:
                self.session_tokens = json.loads(f.read())

                for token in self.session_tokens:
                    os.environ['OP_SESSION_' + token['subdomain']] = token['token']
        else:
            for account in self.config['accounts']:
                subdomain = account['shorthand']
                output = run([self.command, 'signin', subdomain, '--output=raw'], capture_output=True)
                token = output.stdout.decode('utf8').rstrip('\n')
                session_token = { 'subdomain': subdomain, 'token': token }
                self.session_tokens.append(session_token)

            with open(self.session_cache, 'w') as f:
                f.write(json.dumps(self.session_tokens))

    def list_items(self):
        items = []
        for token in self.session_tokens:
            output = run([self.command, 'list', 'items', '--account=' + token['subdomain']], capture_output=True)
            items_subdomain = json.loads(output.stdout.decode('utf8'))
            items += items_subdomain

        return items
