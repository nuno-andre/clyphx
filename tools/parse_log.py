from datetime import datetime
from ast import literal_eval
from platform import system
from pathlib import Path
import os
import re


LINE = re.compile(r'(?P<tag>\S*?)\=(?P<value>.*)')
DTFMT = '%Y-%m-%dT%H:%M:%S.%f'


def get_user_folder():
    if system() == 'Windows':
        return Path(os.environ['APPDATA']) / 'Ableton'
    elif system() == 'Darwin':
        raise NotImplementedError
    else:
        raise NotImplementedError


def get_reports():
    path = get_user_folder() / 'Live Reports/Usage'
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
    report = get_reports()[-1]

    with open(report) as logfile:
        parse_log(logfile.read())


if __name__ == '__main__':
    get_last_report()
