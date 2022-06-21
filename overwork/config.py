import sys
import getopt

from dataclasses import dataclass
from typing import ClassVar

from Xlib.rdb import ResourceDB, SepArg


# Resources identifier
WS_NAME = 'overwork.polybar.{i}'
WS_CLASS = 'Module.Menu.Button'


# Configuration structures
@dataclass
class Parameters:
    args: list

    db_file: bytes = None
    amount: int = 10

    __shorts: ClassVar[str] = 'f:l:'
    __long: ClassVar[list[str]] = ['length=', 'file=']

    def __init__(self, args):
        opts, self.args = getopt.getopt(args, Parameters.__shorts, Parameters.__long)

        for opt, arg in opts:

            if opt in ('-l', '--length'):
                try:
                    self.amount = int(arg)
                    if self.amount <= 0:
                        raise ValueError()
                except ValueError:
                    print(f'! Invalid value for {opt}: "{arg}"')
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

    def __init__(self, db, status, i):

        def name(part):
            tail = f'{status}-{part}'
            return Colors.__WS_COLOR_NAME.format(i=i, fmt=tail)

        self.foreground = db.get(name('foreground'), Colors.__WS_FOREGROUND_CLASS)
        self.background = db.get(name('background'), Colors.__WS_BACKGROUND_CLASS)
        self.overline = db.get(name('overline'), Colors.__WS_OVERLINE_CLASS)
        self.underline = db.get(name('underline'), Colors.__WS_UNDERLINE_CLASS)


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
    database = ResourceDB(file=parameters.db_file)
except IOError:
    print(f'! Invalide resources file: "{parameters.db_file}"')
    sys.exit(1)


# Load workspaces name
ws_names = [database.get(WS_NAME.format(i=i), WS_CLASS) for i in range(parameters.amount)]


# Load formating for the button of each workspaces
ws_formats = [Formating(database, i) for i in range(parameters.amount)]

