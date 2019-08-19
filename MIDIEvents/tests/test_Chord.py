import unittest

from MIDIEvents import Chord, Note, NoteList, Sequence


class TestChord(unittest.TestCase):
    """Generally test using an A4 Major chord, A4, C#5, E5"""
    def test_string(self):
        self.assertEqual(str(Chord.from_ident("A4 Major")), "Chord(A4, C#5, E5)")

    def test_equality(self):
        c1 = Chord(Note(69), Note(73), Note(76))
        c2 = Chord(Note(69), Note(73), Note(76))
        self.assertEqual(c1, c2)
        nl_ordered = NoteList(Note(69), Note(73), Note(76))  # Pre-ordered
        self.assertEqual(nl_ordered, c1)
        nl_unordered = NoteList(Note(73), Note(69), Note(76))  # Un-ordered
        self.assertEqual(nl_unordered, c1)
        seq1 = Sequence(Note(69), Note(73), Note(76))
        self.assertNotEqual(c1, seq1)
        # Different note list lengths should automatically be not equal
        c3 = Chord(Note(69), Note(73), Note(76), Note(100))
        self.assertNotEqual(c1, c3)

    def test_identify(self):
        c1 = Chord.from_ident("A4 Major")
        self.assertIn("A4 Major", c1.identify())
        c2 = Chord()
        self.assertEqual(c2.identify(), None)

    def test_get_semitones(self):
        c1 = Chord.from_ident("A4 Major")
        self.assertEqual(c1._get_semitones(), [0, 4, 7])
    
    def test_from_ident(self):
        c1 = Chord(Note(69), Note(73), Note(76))
        c2 = Chord.from_ident("A4 Major")
        self.assertEqual(c1, c2)
        with self.assertRaises(AssertionError):
            Chord.from_ident("")
        with self.assertRaises(ValueError):
            Chord.from_ident("test test")
        with self.assertRaises(ValueError):  # This is a different error message in _get_semitones_from_chord_name
            Chord.from_ident("A4 test")

    def test_from_note_chord(self):
        c1 = Chord(Note(69), Note(73), Note(76))
        c2 = Chord.from_note_chord(Note(69), "Major")
        self.assertEqual(c1, c2)

    def test_get_semitones_from_chord_name(self):
        self.assertEqual(Chord._get_semitones_from_chord_name("Major"), [0, 4, 7])
        self.assertEqual(Chord._get_semitones_from_chord_name("Harmonic seventh"), [0, 4, 7, 10])
        self.assertEqual(Chord._get_semitones_from_chord_name("Augmented sixth"), [0, 6, 10])  # Multiple possible chord, should select 1st
        with self.assertRaises(ValueError):
            Chord._get_semitones_from_chord_name("test")

    def test_hash(self):
        c1 = Chord(Note(69), Note(73), Note(76))
        self.assertEqual(hash(c1), 643362958232848345)
        self.assertEqual(Chord.__hash__, NoteList.__hash__)
