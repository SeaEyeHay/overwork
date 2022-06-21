from copy import copy
from functools import reduce

import i3ipc


class i3Iter:

    # Constructor
    def __init__(self, file):
        # Load the config used by i3
        if isinstance(file, i3ipc.Connection):
            self.content = file.get_config().config
            self.content = self.content.split('\n')

        # Open the file from the path and read the config
        elif isinstance(file, str):
            with open(file, 'r', encoding='utf-8') as buf:
                self.content = buf.readlines()

        # Read the config from the provided file
        else:
            self.content = file.readlines()

    # Iterator

    def __iter__(self):
        return copy(self)

    def __next__(self):
        # Find the next variable
        while not self.content[0].lstrip().startswith('set'):
            self.content = self.content[1:]

            # End of file
            if not len(self.content) > 0:
                raise StopIteration

        # Extract the variable's "Name" and "Value"
        pair = self.content[0][self.content[0].find('$'):] \
            .rstrip('\n') \
            .split(maxsplit=1)

        # Move to the next line
        self.content = self.content[1:]

        return pair


class i3Dict(dict):

    def expand_value(self, value):

        def extract_word(value):
            for i, cha in enumerate(value):
                if not cha.isalnum() and cha != '$':
                    word = value[:i]
                    value = value[i:]

                    return word, value

        def next_part(value):
            while (i := value.find('$')) >= 0:
                yield value[:i]
                var, value = extract_word(value[i:])
                yield self[var]

            yield value

        return reduce(lambda ex, part: ex + part, next_part(value))


    def insert_var(self, name, value):
        value = self.expand_value(value)
        self[name] = value

