import collections
import logging

from MIDIEvents import NoteList

logger = logging.getLogger("MIDIEvents")


class Sequence(NoteList):
    maxlen = 16  # Max length to compare a deque to

    def __init__(self, *args):
        super().__init__(args)
        if len(self.notes) > self.maxlen:
            raise ValueError(f"Currently only supports Sequences of up to {self.maxlen} notes")
    
    def __eq__(self, other):
        # Get the last n notes if it's a deque, where n is the length of self.notes
        if isinstance(other, collections.deque):  # Assumed to be MIDIEventLoop.recent_notes, a deque of ints
            notes = list(other)[-len(self.notes):]
            other = Sequence(notes)
        if isinstance(other, tuple):
            other = Sequence(other)
        if isinstance(other, self.__class__) or issubclass(self.__class__, other.__class__):  # Needs to be last
            return self.notes == other.notes
        return False

    __hash__ = NoteList.__hash__
