from collections import deque


class ChordProgression:
    maxlen = 32

    def __init__(self, *chords):
        self.chords = tuple(chords)

    def check_deque(self, d: deque):
        """
        It's important to note that every note processed created a new chord.  So the recent_chords deque that this gets
        compared with will have something similar to  [(C4), (C4, E4), (C4, E4, G4)] when a C4 Major chord is played.
        There's 1 Chord object for each note, culminating in a C4 Major chord.  For that reason, the comparison uses
        an ordered non sequential search method.
        """
        if len(self.chords) > len(d):
            return False  # Short circuit when target it too long
        deque_iter = iter(d)
        for c in self.chords:
            try:
                cur_val = next(deque_iter)
                while c != cur_val:
                    cur_val = next(deque_iter)
            except StopIteration:
                return False
        try:
            next(deque_iter)
        except StopIteration:
            return True  # Need to make sure the most recent chord is what we're matching, if there's anything remaining return False
        return False
