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
        self.system = system()

    @property
    def user_folder(self):
        if self.system == 'Windows':
            return Path(os.environ['APPDATA']) / 'Ableton'
        elif self.system == 'Darwin':
            raise NotImplementedError
        else:
            raise NotImplementedError

    @property
    def reports(self):
        path = self.user_folder / 'Live Reports/Usage'
        return list(path.glob('*.log'))


def parse_log(content):
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
        parse_log(logfile.read())


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

    def clean(self, keep=1):
        if len(self.sessions) > keep:
            # TODO: split and remove first sessions
            pass
