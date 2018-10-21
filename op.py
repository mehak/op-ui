#!/usr/bin/python
""" op.py - cli wrapper around op """

import json
import os
from datetime import datetime
from pathlib import Path
from subprocess import run


class OnePassword:
    """ Class responsible for wrapping op """
    def __init__(self, op_path=None):
        self.command = '/usr/bin/op'
        self.namespace = 'win.b1n.op'

        if op_path:
            self.op_path = op_path
        else:
            home = str(Path.home())
            self.op_path = f'{home}/.op'

        self.config_path = f'{self.op_path}/config'
        self.session_cache = f'/tmp/{self.namespace}_session_cache'

        with open(self.config_path) as config_file:
            self.config = json.loads(config_file.read())

        self.session_tokens = []

    def aged_out(self):
        """ Checks the age of the cache """
        now = datetime.now().timestamp()
        atime = os.stat(self.session_cache).st_atime
        mtime = os.stat(self.session_cache).st_mtime
        ctime = os.stat(self.session_cache).st_ctime
        last_access = atime if atime > mtime else mtime
        last_access = ctime if last_access > ctime else last_access

        seconds_since_last_access = now - last_access
        thirty_minutes = 1800

        return seconds_since_last_access >= thirty_minutes

    def signin(self, subdomain='all', use_cache=True):
        """ Either read from a cache or sign-in to all accounts """
        session_cache = self.session_cache
        exists = os.path.isfile(session_cache)
        has_content = exists and os.stat(session_cache).st_size > 3
        if use_cache and has_content and not self.aged_out():
            with open(self.session_cache) as session_file:
                self.session_tokens = json.loads(session_file.read())

                for token in self.session_tokens:
                    subdomain = token['subdomain']
                    tok = token['token']
                    os.environ[f'OP_SESSION_{subdomain}'] = tok
        else:
            self.session_tokens = []
            for account in self.config['accounts']:
                subdomain = account['shorthand']
                command = [self.command, 'signin', subdomain, '--output=raw']
                output = run(command, capture_output=True)

                if output.returncode > 0:
                    raise ChildProcessError(f'{output.stderr.decode("utf8")}')

                token = output.stdout.decode('utf8').rstrip('\n')
                session_token = {'subdomain': subdomain, 'token': token}
                self.session_tokens.append(session_token)

            with open(self.session_cache, 'w') as session_file:
                session_file.write(json.dumps(self.session_tokens))

    def __generic_run(self, arguments):
        """ Helper for running op commands and returning output objects """
        command = [self.command] + arguments
        output = run(command, capture_output=True)

        if output.returncode > 0:
            raise ChildProcessError(f'{output.stderr.decode("utf8")}')

        return json.loads(output.stdout.decode('utf8').rstrip('\n'))

    def __generic_list(self, command, subdomain):
        """ Generic function for getting op lists """
        arguments = ['list', command, '--account=' + subdomain]
        return self.__generic_run(arguments)

    def list(self, command):
        """ Get a list of command for all subdomains """
        valid_commands = ['documents',
                          'groups',
                          'items',
                          'templates',
                          'users',
                          'vaults']

        if command not in valid_commands:
            error_message = f'{command} is not a valid command.'
            advice = f'Approved commands are {valid_commands}'
            message = f'{error_message}  {advice}'
            raise ValueError(message)

        objects = []
        for token in self.session_tokens:
            objects += self.__generic_list(command, token['subdomain'])

        return objects
