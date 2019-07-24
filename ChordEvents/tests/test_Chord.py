import unittest

from ChordEvents import Chord, Note


class Test_Chord(unittest.TestCase):
    """Generally test using an A4 Major chord, A4, C#5, E5"""
    def test_string(self):
        self.assertEqual(str(Chord.from_ident("A4 Major")), "Chord(A4, C#5, E5)")

    def test_equality(self):
        c1 = Chord(Note(69), Note(73), Note(76))
        c2 = Chord(Note(69), Note(73), Note(76))
        self.assertEqual(c1, c2)

    def test_identify(self):
        c1 = Chord.from_ident("A4 Major")
        self.assertIn("A4 Major", c1.identify())

    def test__get_semitones(self):
        c1 = Chord.from_ident("A4 Major")
        self.assertEqual(c1._get_semitones(), [0, 4, 7])
    
    def test_from_ascii(self):
        c1 = Chord(Note(69), Note(73), Note(76))
        c2 = Chord.from_ascii("A4, C#5, E5")
        c3 = Chord.from_ascii("A4 C#5 E5")
        self.assertEqual(c1, c2)
        self.assertEqual(c1, c3)
    
    def test_from_ident(self):
        c1 = Chord(Note(69), Note(73), Note(76))
        c2 = Chord.from_ident("A4 Major")
    
    def test_from_note_chord(self):
        c1 = Chord(Note(69), Note(73), Note(76))
        c2 = Chord.from_note_chord(Note(69), "Major")
        self.assertEqual(c1, c2)
    
    def test_from_midi_list(self):
        c1 = Chord(Note(69), Note(73), Note(76))
        c2 = Chord.from_midi_list([69, 73, 76])
        self.assertEqual(c1, c2)

    def test_get_semitones_from_chord_name(self):
        self.assertEqual(Chord._get_semitones_from_chord_name("Major"), [0, 4, 7])
        self.assertEqual(Chord._get_semitones_from_chord_name("Harmonic seventh"), [0, 4, 7, 10])
        self.assertEqual(Chord._get_semitones_from_chord_name("Augmented sixth"), [0, 6, 10])  # Multiple possible chord, should select 1st
    
    def test_parse_note_args(self):
        with self.assertRaises(AssertionError):
            Chord._parse_note_args(1)
        with self.assertRaises(TypeError):
            Chord._parse_note_args(tuple([1, 2]))
