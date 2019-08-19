import collections
from unittest import TestCase

from MIDIEvents import Note, Sequence, NoteList, Chord


class TestSequence(TestCase):
    def test_init(self):
        expected = (Note(5), Note(7))
        seq1 = Sequence(Note(5), Note(7))
        self.assertEqual(seq1.notes, expected)
        seq2 = Sequence((Note(5), Note(7)))
        self.assertEqual(seq2.notes, expected)
        seq3 = Sequence(expected)
        self.assertEqual(seq3.notes, expected)

    def test_sequence_length(self):
        with self.assertRaises(ValueError):
            Sequence.from_midi_list(list(range(Sequence.maxlen + 1)))

    def test_eq_tuple(self):
        notes = (Note(15), Note(10), Note(20))
        seq1 = Sequence(notes)
        self.assertEqual(seq1, notes)

    def test_eq_chord(self):
        notes = (Note(15), Note(10), Note(20))
        seq1 = Sequence(notes)
        c1 = Chord(notes)
        self.assertNotEqual(seq1, c1)  # Chord should sort the notes, while Sequence doesn't

    def test_eq_sequence(self):
        notes = (Note(15), Note(10), Note(20))
        seq1 = Sequence(notes)
        seq2 = Sequence.from_midi_list([15, 10, 20])
        self.assertEqual(seq1, seq2)

    def test_eq_deque(self):
        notes = (Note(15), Note(10), Note(20))
        seq1 = Sequence(notes)
        notes_deque = collections.deque()
        notes_deque.append(Note(50))  # Fill with some junk first
        notes_deque.append(Note(50))
        notes_deque.append(Note(50))
        for n in notes:
            notes_deque.append(n)
        self.assertEqual(seq1, notes_deque)

    def test_eq_notelist(self):
        notes = (Note(15), Note(10), Note(20))
        seq1 = Sequence(notes)
        nl1 = NoteList(notes)
        self.assertEqual(seq1, nl1)

    def test_hash(self):
        seq1 = Sequence(Note(69), Note(73), Note(76))
        self.assertEqual(hash(seq1), 643362958232848345)
        self.assertEqual(Sequence.__hash__, NoteList.__hash__)
