import collections
from unittest import TestCase

from MIDIEvents import Chord, ChordSequence


class TestChordSequence(TestCase):
    def setUp(self) -> None:
        # Just some chords that are available
        self.c1 = Chord.from_ident("A1 Major")
        self.c2 = Chord.from_ident("A2 Major")
        self.c3 = Chord.from_ident("A3 Major")

    def test_init(self):
        cs1 = ChordSequence(self.c1, self.c2, self.c3)
        self.assertEqual(cs1.chords, (self.c1, self.c2, self.c3))

    def test_check_deque(self):
        cs1 = ChordSequence(self.c1, self.c2, self.c3)
        d = collections.deque([self.c1, self.c2, self.c3])
        self.assertTrue(cs1.check_deque(d))
        d.append(Chord.from_ident("A4 Major"))
        self.assertFalse(cs1.check_deque(d))
