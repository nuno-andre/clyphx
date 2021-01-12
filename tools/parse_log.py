#! /usr/bin/env python3

from datetime import datetime
from ast import literal_eval
from platform import system
from pathlib import Path
import logging
import os
import re


log = logging.getLogger(__name__)

LINE = re.compile(r'(?P<tag>\S*?)\=(?P<value>.*)')
DTFMT = '%Y-%m-%dT%H:%M:%S.%f'


class Environment:
    def __init__(self):
        if system() == 'Windows':
            self.mac = False
        elif system() == 'Darwin':
            self.mac = True
        else:
            raise NotImplementedError

    @property
    def user_folder(self):
        if not self.mac:
            return Path(os.environ['APPDATA']) / 'Ableton'
        else:
            raise NotImplementedError

    @property
    def app_folder(self):
        '''Returns Ableton Live folder.'''
        if self.mac:
            raise NotImplementedError
        else:
            if not getattr(self, '_app_folder', None):
                import winreg

                reg = winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT)
                value = winreg.QueryValue(reg, r'ableton\Shell\open\command')
                path, _ = value.rsplit(' ', 1)
                self._app_folder = Path(path).parents[1]
            return self._app_folder

    @property
    def reports(self):
        path = self.user_folder / 'Live Reports/Usage'
        return list(path.glob('*.log'))

    @property
    def resources(self):
        folder = 'Contents/App-Resources' if self.mac else 'Resources'
        return self.app_folder / folder


def parse_report(content):
    info = dict()
    logs = list()

    for line in content.splitlines():
        data = LINE.search(line).groupdict()
        try:
            dt = datetime.strptime(data['tag'], DTFMT)
            logger, *msg = data['value'].split(' ', 1)
            msg = literal_eval(msg[0]) if msg else None
            logs.append((dt, logger, msg))

        except ValueError:
            info.update({data['tag']: data['value']})

    return {'info': info, 'logs': logs}


def get_last_report():
    env = Environment()
    report = env.reports()[-1]

    with open(report) as logfile:
        return parse_report(logfile.read())


TIMESTAMP = r'(?P<timestamp>[T0-9\-\:\.])'
LEVEL = r'(?P<level>[a-z])'
LOG_LINE = re.compile(r'^{}:\s{}:\s(?P<message>.*)$'.format(TIMESTAMP, LEVEL), re.M)
START_LOG = re.compile(r'^{}: info: Started: Live .*$'.format(TIMESTAMP))


class SessionLog:
    def __init__(self, start):
        self.start = start
        self.logs = list()

    def append(self, log):
        self.logs.append(log)


class LogFile:
    def __init__(self):
        self.sessions = list()

    def parse(self, path):
        raise NotImplementedError

        session = None

        for line in open(path):
            line = LOG_LINE.match(line).groupdict()
            if line['message'].startswith('Started: Live '):
                if session:
                    self.sessions.append(session)
                session = SessionLog(start=line['timestamp'])
            if not session:
                # lines without previous start log
                continue
            session.append(line)


def rotate_logfile():
    env = Environment()
    NUM = re.compile(r'Log.(\d*).txt')

    for path in env.user_folder.glob('*/**'):
        if path.name == 'Preferences':
            last = 0
            for logfile in path.glob('Log*.txt'):
                num = NUM.match(logfile.name)
                if num:
                    last = max(last, int(num.group(1)))
            dest = path / f'Log.{last+1}.txt'
            try:
                path.joinpath('Log.txt').rename(dest)
            except PermissionError:
                log.error('Cannot rotate log. Is Live running?')
            else:
                log.info('Log rotated. Last logs moved to: %s', dest)
