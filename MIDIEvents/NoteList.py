import logging

from MIDIEvents import Note

logger = logging.getLogger("MIDIEvents")


class NoteList:
    max_depth = 5  # Max depth to search for notes

    def __init__(self, *args):
        try:
            for _ in range(self.max_depth):
                if isinstance(args, NoteList):  # NoteList
                    self.notes = args.notes
                    return
                if all(isinstance(x, Note) for x in args):  # Note
                    self.notes = args  # Triggers the setter
                    return
                if all(isinstance(x, int) for x in args):  # int, assumed MIDI representation
                    self.notes = [Note(x) for x in args]
                    return
                args = args[0]  # Go one level deeper
            else:
                raise ValueError(f"Illegal configuration of notes, got '{type(args)}'")
        except TypeError:
            raise TypeError(f"Expected iterable of Notes or NoteList, got '{type(args)}'")

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join(str(x) for x in self.notes) + ")"

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return hash(self.notes)

    def __eq__(self, other):
        return self.notes == other.notes

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, notes):
        self._notes = tuple(sorted(notes))

    @classmethod
    def from_ascii(cls, note_string):  # TODO note_string is similar to note_str in the Note class, maybe rename this?
        note_string = note_string.replace(",", "")
        return cls([Note(x) for x in note_string.split(" ")])
    
    @classmethod
    def from_midi_list(cls, midi_list):
        return cls([Note(x) for x in midi_list])
