import logging

from MIDIEvents import Note

logger = logging.getLogger("MIDIEvents")


class NoteList:
    """Base class that other note lists (e.g. ``Chord`` or ``Sequence``) inherit from.
    
    Attributes:
        notes: Tuple of ``Note`` objects
        max_depth: Default 3.  Class attribute.  Max depth to search for notes in input args.
    
    Args:
        *args: Iterable of ``Note`` objects or multiple ``Note`` objects passed to constructor.  Also accepts a NoteList object.
    """
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
    def from_ascii(cls, note_string):
        """Used to create a ``NoteList`` or child class from a string of notes.
        
        Args:
            note_string: Space or comma-space separated ASCII notes
        """
        note_string = note_string.replace(",", "")
        return cls([Note(x) for x in note_string.split(" ")])
    
    @classmethod
    def from_midi_list(cls, midi_list):
        """Used to create a ``NoteList`` or child class from a list of MIDI codes
        
        Args:
            midi_list: List of integers represnting MIDI note codes"""
        return cls([Note(x) for x in midi_list])
