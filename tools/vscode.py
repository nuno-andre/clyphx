#! /usr/bin/env python3
from pathlib import Path
from shutil import which
import logging
import json
import os
try:
    from .parse_log import Environment
except ImportError:
    from parse_log import Environment

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

BASEDIR = Path(__file__).parents[1]
TEMPLATE = BASEDIR / '.vscode/.settings.json'


class Settings:
    def __init__(self):
        self._config = json.loads(TEMPLATE.read_text())
        self.env = Environment()
        self.set_python_path()
        self.set_lib_paths()
        self.set_formatter()
        self.set_linter()

    @property
    def config(self):
        cfg = {k: v for k, v in sorted(self._config.items()) if k[0] != '['}
        cfg.update({k: dict(sorted(v.items())) for k, v in self._config.items() if k[0] == '['})
        return cfg

    def set_python_path(self):
        path = BASEDIR / '.bin/python.exe'

        if path.is_file():
            path = '${workspaceFolder}/.bin'
        else:
            path = which('python27')
            if not path:
                log.error('python2.7 executable not found')
                return
            path = Path(path).parent.as_posix()

        log.warning('Python 2.7 runtime found in %s', path)
        self._config['python.pythonPath'] = path

    def set_lib_paths(self):
        key = 'osx' if self.env.mac else 'windows'

        paths = [
            '${workspaceFolder}/src/clyphx',
            self.env.resources / 'Python/lib',
            *list(self.env.resources.joinpath('Python/site-packages').iterdir()),
            self.env.resources / 'Python/abl.live',
            self.env.resources / 'MIDI Remote Scripts',
        ]

        self._config.update({
            'python.autoComplete.extraPaths': list(map(str, paths)),
            'python.analysis.extraPaths': list(map(str, paths)),
            'terminal.integrated.env.{}'.format(key): {
                'PATH': os.pathsep.join(['${workspaceFolder}/.bin', '${env:PATH}']),
                'PYTHONPATH': os.pathsep.join(map(str, paths)),
            }
        })

        env = BASEDIR / '.env'
        env.write_text('PYTHONPATH={}'.format(os.pathsep.join(map(str, paths))))
        log.warning('.env file saved in %s', env)

    def set_linter(self):
        '''Add linting (flake8) configuration to VSCode.

        Specific settings are managed in setup.cfg.
        '''
        path = which('flake8')
        if path:
            path = Path(path).as_posix()
            self._config.update({
                'python.linting.flake8Enabled': True,
                'python.linting.flake8Path': path,
            })
            log.warning('Linter found in %s', path)
        else:
            log.error('flake8 executable not found')

    def set_formatter(self):
        '''Add formatting (brunette) configuration to VSCode.

        Specific settings are managed in setup.cfg.
        '''
        path = which('brunette')
        if path:
            path = Path(path).as_posix()
            self._config.update({
                'python.formatting.provider': 'black',
                'python.formatting.blackArgs': [],
                'python.linting.flake8Path': path,
            })
            log.warning('Formatter found in %s', path)
        else:
            log.error('brunette executable not found')

    @property
    def json(self):
        return json.dumps(self.config,
                          ensure_ascii=False,
                          sort_keys=False,
                          indent=2)
    def write(self):
        filepath = TEMPLATE.with_name('settings.json')
        filepath.write_text(self.json)
        log.warning('Configuration saved in %s', filepath)


if __name__ == '__main__':
    conf = Settings()
    conf.write()
