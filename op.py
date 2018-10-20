#!/usr/bin/python

import json
from pathlib import Path
from subprocess import run, PIPE

class OnePassword:
    def __init__(self, config_path=None):
        if (config_path):
            self.config_path = config_path
        else:
            home = str(Path.home())
            self.config_path = home + '/.op/config'

        with open(self.config_path) as f:
            self.config = json.loads(f.read())

        self.session_tokens = []
