import logging
import time
import unittest
import unittest.mock

import mido

from MIDIEvents import Chord, Sequence, MIDIEventLoop, LoopbackPort, Note, ChordProgression

# Prevents a race condition while testing with a non-callback backend.  Runs on both to make inheritance easier.
# Can run as low as 0.005, but lots of stdout content or other lag can cause problems.
# Since it only delays once per test function, a higher value isn't too costly at this time.
TEST_CHORD_DELAY = 0.05

logger = logging.getLogger("MIDIEvents")
logger.setLevel(logging.ERROR)


def press_chord(loopback, chord_obj, direction=None):
    if direction is None:
        direction = "downup"
    if "down" in direction:
        for note in chord_obj.notes:
            loopback.send(mido.Message("note_on", note=note.midi))
    if "up" in direction:
        for note in chord_obj.notes:
            loopback.send(mido.Message("note_off", note=note.midi))
    time.sleep(TEST_CHORD_DELAY)


def press_sequence(loopback, sequence_obj):
    for note in sequence_obj.notes:
        loopback.send(mido.Message("note_on", note=note.midi))
        loopback.send(mido.Message("note_off", note=note.midi))
    time.sleep(TEST_CHORD_DELAY)


class MIDIEventLoop_base_tests:
    """To be inherited from.  Override ``setUp`` and ``tearDown``"""

    def test_decorator_string(self):
        mock = unittest.mock.Mock()
        self.assertFalse(self.MEL.handlers)  # Empty

        @self.MEL.on_notes("C4 Major")
        def sub():  # pragma: no cover
            mock()

        self.assertTrue(self.MEL.handlers)  # Not empty
        press_chord(self.loopback, Chord.from_ident("C4 Major"))
        mock.assert_called()

    def test_decorator_chord(self):
        mock = unittest.mock.Mock()
        self.assertFalse(self.MEL.handlers)  # Empty

        c1 = Chord(Note(5), Note(10), Note(15))

        @self.MEL.on_notes(c1)
        def sub():
            mock()

        self.assertTrue(self.MEL.handlers)  # Not empty
        press_chord(self.loopback, c1)
        mock.assert_called()

    def test_decorator_sequence(self):
        mock = unittest.mock.Mock()
        self.assertFalse(self.MEL.handlers)  # Empty

        seq1 = Sequence(Note(5), Note(10), Note(15))

        @self.MEL.on_notes(seq1)
        def sub():
            mock()

        press_sequence(self.loopback, seq1)
        self.assertTrue(self.MEL.handlers)  # Not empty
        mock.assert_called()

    def test_chord_handlers_add_remove(self):
        mock1 = unittest.mock.Mock()
        mock2 = unittest.mock.Mock()
        c1 = Chord.from_ident("C4 Major")
        c2 = Chord.from_ident("C5 Minor")
        self.assertFalse(self.MEL.handlers)  # Empty
        self.MEL.add_handler(mock1, c1)
        self.assertTrue(self.MEL.handlers)  # Not empty
        self.MEL.clear_handlers()
        self.assertFalse(self.MEL.handlers)
        # Now test a single removal
        self.MEL.add_handler(mock1, c1)
        self.MEL.add_handler(mock2, c2)
        self.assertTrue(self.MEL.handlers)  # Not empty
        self.assertIn(c1, self.MEL.handlers)
        self.assertIn(c2, self.MEL.handlers)
        self.MEL.clear_handlers(c1)
        self.assertNotIn(c1, self.MEL.handlers)
        self.assertIn(c2, self.MEL.handlers)

    def test_handler_remove_class(self):
        mock1 = unittest.mock.Mock()
        mock2 = unittest.mock.Mock()
        c1 = Chord.from_ident("C4 Major")
        s1 = Sequence.from_midi_list([1, 2, 3])
        self.MEL.add_handler(mock1, c1)
        self.MEL.add_handler(mock2, s1)
        self.assertIn(c1, self.MEL.handlers)
        self.assertIn(s1, self.MEL.handlers)
        self.MEL.clear_handlers(Chord)
        self.assertNotIn(c1, self.MEL.handlers)
        self.assertIn(s1, self.MEL.handlers)

    def test_sequence_handlers_add_remove(self):
        mock1 = unittest.mock.Mock()
        mock2 = unittest.mock.Mock()
        seq1 = Sequence(Note(1), Note(2), Note(3))
        seq2 = Sequence(Note(4), Note(5), Note(6))
        self.assertFalse(self.MEL.handlers)  # Empty
        self.MEL.add_handler(mock1, seq1)
        self.assertTrue(self.MEL.handlers)  # Not empty
        self.MEL.clear_handlers()
        self.assertFalse(self.MEL.handlers)
        # Now test a single removal
        self.MEL.add_handler(mock1, seq1)
        self.MEL.add_handler(mock2, seq2)
        self.assertTrue(self.MEL.handlers)  # Not empty
        self.assertIn(seq1, self.MEL.handlers)
        self.assertIn(seq2, self.MEL.handlers)
        self.MEL.clear_handlers(seq1)
        self.assertNotIn(seq1, self.MEL.handlers)
        self.assertIn(seq2, self.MEL.handlers)

    def test_note_on(self):
        """Test that notes are released when a 0 velocity ``note_on`` message is received"""
        self.loopback.send(mido.Message("note_on", note=60))  # C4
        self.loopback.send(mido.Message("note_on", note=64))  # E4
        self.loopback.send(mido.Message("note_on", note=67))  # G4
        time.sleep(TEST_CHORD_DELAY)
        self.assertTrue(self.MEL.down_notes)  # assert not empty

        self.loopback.send(mido.Message("note_on", note=60, velocity=0))
        self.loopback.send(mido.Message("note_on", note=64, velocity=0))
        self.loopback.send(mido.Message("note_on", note=67, velocity=0))
        time.sleep(TEST_CHORD_DELAY)
        self.assertFalse(self.MEL.down_notes)  # assert empty

    def test_note_off(self):
        """Test that notes are release when the ``note_off`` message is received"""
        self.loopback.send(mido.Message("note_on", note=60))  # C4
        self.loopback.send(mido.Message("note_on", note=64))  # E4
        self.loopback.send(mido.Message("note_on", note=67))  # G4
        time.sleep(TEST_CHORD_DELAY)
        self.assertTrue(self.MEL.down_notes)  # assert not empty
        
        self.loopback.send(mido.Message("note_off", note=60))
        self.loopback.send(mido.Message("note_off", note=64))
        self.loopback.send(mido.Message("note_off", note=67))
        time.sleep(TEST_CHORD_DELAY)
        self.assertFalse(self.MEL.down_notes)  # assert empty

    def test_trigger_on_custom_chord(self):
        mock = unittest.mock.Mock()
        chord = Chord.from_midi_list([20, 40, 60])
        self.assertFalse(self.MEL.handlers)  # Empty check
        self.MEL.add_handler(mock, chord)

        press_chord(self.loopback, chord)
        mock.assert_called()

    def test_trigger_on_sequence(self):
        mock = unittest.mock.Mock()
        seq1 = Sequence(Note(1), Note(2), Note(3))
        self.assertFalse(self.MEL.handlers)  # Empty check
        self.MEL.add_handler(mock, seq1)

        press_sequence(self.loopback, seq1)
        mock.assert_called()
    
    def test_multiple_callbacks_different_chords(self):
        mock1 = unittest.mock.Mock()
        mock2 = unittest.mock.Mock()
        c1 = Chord(Note(20), Note(40), Note(60))
        c2 = Chord(Note(30), Note(40), Note(50))
        self.MEL.add_handler(mock1, c1)
        self.MEL.add_handler(mock2, c2)

        press_chord(self.loopback, c1)
        mock1.assert_called()
        mock2.assert_not_called()

        press_chord(self.loopback, c2)
        mock2.assert_called()

    def test_multiple_callbacks_same_chord(self):
        mock1 = unittest.mock.Mock()
        mock2 = unittest.mock.Mock()
        c1 = Chord(Note(20), Note(40), Note(60))
        c2 = Chord(Note(20), Note(40), Note(60))
        self.MEL.add_handler(mock1, c1)
        self.MEL.add_handler(mock2, c2)

        press_chord(self.loopback, c1)
        mock1.assert_called()
        mock2.assert_called()

    def test_multiple_callbacks_different_sequence(self):
        mock1 = unittest.mock.Mock()
        mock2 = unittest.mock.Mock()
        seq1 = Sequence(Note(20), Note(40), Note(60))
        seq2 = Sequence(Note(30), Note(40), Note(50))
        self.MEL.add_handler(mock1, seq1)
        self.MEL.add_handler(mock2, seq2)

        press_sequence(self.loopback, seq1)
        mock1.assert_called()
        mock2.assert_not_called()

        press_sequence(self.loopback, seq2)
        mock2.assert_called()

    def test_multiple_callbacks_same_sequence(self):
        mock1 = unittest.mock.Mock()
        mock2 = unittest.mock.Mock()
        seq1 = Sequence(Note(20), Note(40), Note(60))
        seq2 = Sequence(Note(20), Note(40), Note(60))
        self.MEL.add_handler(mock1, seq1)
        self.MEL.add_handler(mock2, seq2)

        press_sequence(self.loopback, seq1)
        mock1.assert_called()
        mock2.assert_called()

    def test_chord_and_sequence(self):
        chord_mock = unittest.mock.Mock()
        sequence_mock = unittest.mock.Mock()
        c1 = Chord(Note(1), Note(2), Note(3))
        seq1 = Sequence(Note(1), Note(2), Note(3))
        self.MEL.add_handler(chord_mock, c1)
        self.MEL.add_handler(sequence_mock, seq1)
        press_chord(self.loopback, c1)  # Should trigger both
        chord_mock.assert_called()
        sequence_mock.assert_called()

    def test_chord_progression_add_remove(self):
        c1 = Chord.from_ident("A1 Major")
        c2 = Chord.from_ident("A2 Major")
        c3 = Chord.from_ident("A3 Major")
        cs1 = ChordProgression(c1, c2, c3)
        mock = unittest.mock.Mock()
        self.MEL.add_handler(mock, cs1)
        self.assertTrue(self.MEL.handlers)
        self.MEL.clear_handlers()
        self.assertFalse(self.MEL.handlers)

    def test_chord_progression_callback(self):
        c1 = Chord.from_ident("A1 Major")
        c2 = Chord.from_ident("A2 Major")
        c3 = Chord.from_ident("A3 Major")
        cs1 = ChordProgression(c1, c2, c3)
        mock = unittest.mock.Mock()
        self.MEL.add_handler(mock, cs1)
        press_chord(self.loopback, c1)
        press_chord(self.loopback, c2)
        press_chord(self.loopback, c3)
        time.sleep(TEST_CHORD_DELAY)
        mock.assert_called()

    def test_chord_progression_multiple_callback(self):
        c1 = Chord.from_ident("A1 Major")
        c2 = Chord.from_ident("A2 Major")
        c3 = Chord.from_ident("A3 Major")
        c4 = Chord.from_ident("C1 Major")
        c5 = Chord.from_ident("C2 Major")
        c6 = Chord.from_ident("C3 Major")
        cs1 = ChordProgression(c1, c2, c3)
        cs2 = ChordProgression(c4, c5, c6)
        mock1 = unittest.mock.Mock()
        mock2 = unittest.mock.Mock()
        self.MEL.add_handler(mock1, cs1)
        self.MEL.add_handler(mock2, cs2)
        press_chord(self.loopback, c1)
        press_chord(self.loopback, c2)
        press_chord(self.loopback, c3)
        time.sleep(TEST_CHORD_DELAY)
        mock1.assert_called()
        press_chord(self.loopback, c4)
        press_chord(self.loopback, c5)
        press_chord(self.loopback, c6)
        time.sleep(TEST_CHORD_DELAY)
        mock2.assert_called()


    def test_no_ports(self):
        with self.assertRaises(RuntimeError):
            MIDIEventLoop()

    def test_invalid_port(self):
        with self.assertRaises(TypeError):
            MIDIEventLoop(port=5)


class TestMIDIEventLoop_rtmidi(unittest.TestCase, MIDIEventLoop_base_tests):
    def setUp(self):
        self.loopback = LoopbackPort()
        mido.set_backend("mido.backends.rtmidi", load=True)
        self.MEL = MIDIEventLoop(port=self.loopback)
    
    def test_warn_on_callbacks_enabled(self):
        """Test specific to a backend that supports callbacks"""
        with self.assertLogs(logger=logger, level="WARNING"):
            self.MEL.start()
        with self.assertLogs(logger=logger, level="WARNING"):
            self.MEL.stop()


class TestMIDIEventLoop_pygame(unittest.TestCase, MIDIEventLoop_base_tests):
    def setUp(self):
        self.loopback = LoopbackPort()
        mido.set_backend("mido.backends.pygame", load=True)
        self.MEL = MIDIEventLoop(port=self.loopback)
        self.MEL.start()

    def tearDown(self):
        self.MEL.stop()
