import unittest

from ChordEvents import Note


class Test_Note(unittest.TestCase):

    def test_init(self):
        self.assertEqual(Note("A4").midi, 69)
        self.assertEqual(Note("Cb4").midi, 59)  # Underflow and decrement the octave
        self.assertEqual(Note("F#2").midi, 42)
        self.assertEqual(Note("F#10").midi, 138)

        self.assertEqual(Note("A", 4).midi, 69)
        self.assertEqual(Note("Cb", 4).midi, 59)
        self.assertEqual(Note("F#", 2).midi, 42)

        self.assertEqual(Note(69).pc, 9)
        self.assertEqual(Note(69).octave, 4)

        with self.assertRaises(TypeError):
            Note([])

    def test_string(self):
        n1 = Note("A4")
        self.assertEqual(str(n1), "A4")
    
    def test_repr(self):
        n1 = Note("A4")
        self.assertEqual(repr(n1), "Note(A4)")
    
    def test_greater_than(self):
        n1 = Note(69)
        n2 = Note(70)
        self.assertGreater(n2, n1)
        self.assertGreater(n2.midi, n1.midi)
    
    def test_equality(self):
        n1 = Note("A4")
        n2 = Note(69)
        self.assertEqual(n1, n2)