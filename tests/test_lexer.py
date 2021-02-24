# from __future__ import absolute_import, unicode_literals

# from pathlib import Path
# import sys

# here = Path(__file__).parents[1].joinpath('src/clyphx')
# sys.path.insert(0, str(here))

# import re
# from collections import ChainMap
# from vendor.retoken import Scanner
# from core.tokens import OBJECT, VIEW, ACTION, CONTINOUS_PARAM_VALUE, IDENTIFIER


# ACTIONS = [
#     'ADDAUDIO 10',
# ]


# def test_sth():
#     LEXICON = ChainMap(OBJECT, VIEW, ACTION, CONTINOUS_PARAM_VALUE, IDENTIFIER)

#     scanner = Scanner(LEXICON.items(), flags=re.I)

#     for action in ACTIONS:
#         for token, match in scanner.scan_with_holes(action):
#             if token:
#                 print(token, match.group())
