from unittest import TestCase

from MIDIEvents import Note, NoteList


class TestNoteList(TestCase):
    def test_init_from_iter(self):
        nl1 = NoteList(Note(5), Note(7))
        self.assertEqual(nl1._notes, (Note(5), Note(7)))
        nl2 = NoteList([Note(5), Note(7)])
        self.assertEqual(nl2._notes, (Note(5), Note(7)))

    def test_init_from_NoteList(self):
        nl1 = NoteList(Note(5), Note(7))
        self.assertEqual(NoteList(nl1), nl1)

    def test_init_from_int(self):
        nl1 = NoteList(1, 2, 3)
        nl2 = NoteList(Note(1), Note(2), Note(3))
        self.assertEqual(nl1, nl2)

    def test_init_errors(self):
        pass
        with self.assertRaises(ValueError):
            notes = (Note(1), Note(2), Note(3))
            for _ in range(NoteList.max_depth + 1):
                notes = [notes]
            NoteList(notes)
        with self.assertRaises(TypeError):  # Expected iterable of Notes or NoteList
            NoteList(object())

    def test_from_ascii(self):
        expected = (Note(69), Note(73), Note(76))
        nl1 = NoteList.from_ascii("A4, C#5, E5")
        nl2 = NoteList.from_ascii("A4 C#5 E5")
        self.assertEqual(nl1.notes, expected)
        self.assertEqual(nl2.notes, expected)

    def test_from_midi_list(self):
        nl1 = NoteList.from_midi_list([69, 73, 76])
        self.assertEqual(nl1.notes, (Note(69), Note(73), Note(76)))

    def test_hash(self):
        notes = (Note(10), Note(15), Note(20))  # Sorted to emulate NoteList.notes setter method
        nl1 = NoteList(notes)
        self.assertEqual(hash(notes), hash(nl1))
