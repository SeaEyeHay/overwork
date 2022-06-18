import sys
import getopt

from dataclasses import dataclass
from typing import ClassVar

import Xlib.rdb


# Resources identifier
WS_NAME = 'overwork.polybar.{i}'
WS_CLASS = 'Module.Menu.Button'


# Configuration structures
@dataclass
class Parameters:
    db_file: bytes = None
    amount: int = 10

    __shorts: ClassVar[str] = 'f:l:'
    __long: ClassVar[list[str]] = ['length=', 'file=']

    def __init__(self, args):
        opts, args = getopt.getopt(args, Parameters.__shorts, Parameters.__long)

        for opt, arg in opts:

            if opt in ('-l', '--length'):
                try:
                    self.amount = int(arg)
                    if self.amount <= 0:
                        raise ValueError()
                except ValueError:
                    print('! Invalid value for {opt}: "{val}"'.format(opt=opt, val=arg))
                    sys.exit(1)

            elif opt in ('-f', '--file'):
                self.db_file = bytes(arg, 'utf-8')


@dataclass
class Colors:
    foreground: str
    background: str
    overline: str
    underline: str

    __WS_FOREGROUND_CLASS: ClassVar = f'{WS_CLASS}.Foreground'
    __WS_BACKGROUND_CLASS: ClassVar = f'{WS_CLASS}.Background'
    __WS_OVERLINE_CLASS: ClassVar = f'{WS_CLASS}.Overline'
    __WS_UNDERLINE_CLASS: ClassVar = f'{WS_CLASS}.Underline'

    __WS_COLOR_NAME = 'overwork.polybar.{i}.{fmt}'

    def __init__(self, db, st, i):

        def name(part):
            tail = '{status}-{part}'.format(status=st, part=part)
            return Colors.__WS_COLOR_NAME.format(i=i, fmt=tail)

        self.foreground = db[(name('foreground'), Colors.__WS_FOREGROUND_CLASS)]
        self.background = db[(name('background'), Colors.__WS_BACKGROUND_CLASS)]
        self.overline = db[(name('overline'), Colors.__WS_OVERLINE_CLASS)]
        self.underline = db[(name('underline'), Colors.__WS_UNDERLINE_CLASS)]


@dataclass
class Formating:
    exist: Colors
    no_exist: Colors
    focused: Colors
    urgent: Colors

    def __init__(self, db, i):
        self.exist = Colors(db, 'exist', i)
        self.no_exist = Colors(db, 'noexist', i)
        self.focused = Colors(db, 'focused', i)
        self.urgent = Colors(db, 'urgent', i)


# Read command line argument
parameters = Parameters(sys.argv[1:])


# Load the Xresources database
try:
    database = Xlib.rdb.ResourceDB(file=parameters.db_file)
except IOError:
    print('! Invalide resources file: "{path}"'.format(path=parameters.db_file))
    sys.exit(1)


__KEY_ERR = '! No entry found in database for "{n}" or "{c}"'

# Load workspaces name
try:
    ws_names = [database[(WS_NAME.format(i=i), WS_CLASS)] for i in range(parameters.amount)]
except KeyError as ex:
    ex = ex.args[0]
    print(__KEY_ERR.format(n=ex[0], c=ex[1]))
    sys.exit(1)


# Load formating for the button of each workspaces
try:
    ws_formats = [Formating(database, i) for i in range(parameters.amount)]
except KeyError as ex:
    ex = ex.args[0]
    print(__KEY_ERR.format(n=ex[0], c=ex[1]))
    sys.exit(1)

