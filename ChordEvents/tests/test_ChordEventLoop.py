import logging
import queue
import time
import unittest
import unittest.mock

import mido

from ChordEvents import Chord, ChordEventLoop, LoopbackPort, Note

# Prevents a race condition while testing with a non-callback backend.  Runs on both to make inheritance easier.
# Can run as low as 0.005, but lots of stdout content or other lag can cause problems.
# Since it only delays once per test function, a higher value isn't too costly at this time.
TEST_CHORD_DELAY = 0.1

logger = logging.getLogger("ChordEvents")


def press_chord(loopback, chord_obj, direction=None):
    if direction is None:
        direction = "downup"
    if "down" in direction:
        for note in chord_obj.notes:
            loopback.send(mido.Message("note_on", note=note.midi))
    if "up" in direction:
        for note in chord_obj.notes:
            loopback.send(mido.Message("note_off", note=note.midi))


class ChordEventLoop_base_tests:
    """To be inherited.  Override ``setUp`` and ``tearDown``"""
    
    def test_handlers_add_remove(self):
        mock = unittest.mock.Mock()
        self.assertFalse(self.CEL.handlers)  # Empty
        self.CEL.add_chord_handler(mock, "C4 Major")
        self.assertTrue(self.CEL.handlers)  # Not empty
        self.CEL.clear_handlers()
        self.assertFalse(self.CEL.handlers)

    def test_note_on(self):
        """Test that notes are released when a 0 velocity ``note_on`` message is received"""
        self.loopback.send(mido.Message("note_on", note=60))  # C4
        self.loopback.send(mido.Message("note_on", note=64))  # E4
        self.loopback.send(mido.Message("note_on", note=67))  # G4
        time.sleep(TEST_CHORD_DELAY)
        self.assertTrue(self.CEL.down_notes)  # assert not empty

        self.loopback.send(mido.Message("note_on", note=60, velocity=0))
        self.loopback.send(mido.Message("note_on", note=64, velocity=0))
        self.loopback.send(mido.Message("note_on", note=67, velocity=0))
        time.sleep(TEST_CHORD_DELAY)
        self.assertFalse(self.CEL.down_notes)  # assert empty

    def test_note_off(self):
        """Test that notes are release when the ``note_off`` message is received"""
        self.loopback.send(mido.Message("note_on", note=60))  # C4
        self.loopback.send(mido.Message("note_on", note=64))  # E4
        self.loopback.send(mido.Message("note_on", note=67))  # G4
        time.sleep(TEST_CHORD_DELAY)
        self.assertTrue(self.CEL.down_notes)  # assert not empty
        
        self.loopback.send(mido.Message("note_off", note=60))
        self.loopback.send(mido.Message("note_off", note=64))
        self.loopback.send(mido.Message("note_off", note=67))
        time.sleep(TEST_CHORD_DELAY)
        self.assertFalse(self.CEL.down_notes)  # assert empty

    def test_trigger_on_custom_chord(self):
        mock = unittest.mock.Mock()
        chord = Chord.from_midi_list([20, 40, 60])
        self.assertFalse(self.CEL.handlers)  # Empty check
        self.CEL.add_chord_handler(mock, chord)

        press_chord(self.loopback, chord)

        time.sleep(TEST_CHORD_DELAY)
        mock.assert_called()
    
    def test_multiple_callbacks(self):
        mock1 = unittest.mock.Mock()
        mock2 = unittest.mock.Mock()
        c1 = Chord(Note(20), Note(40), Note(60))
        c2 = Chord(Note(30), Note(40), Note(50))
        self.CEL.add_chord_handler(mock1, c1)
        self.CEL.add_chord_handler(mock2, c2)

        press_chord(self.loopback, c1)
        time.sleep(TEST_CHORD_DELAY)
        mock1.assert_called()

        press_chord(self.loopback, c2)
        time.sleep(TEST_CHORD_DELAY)
        mock2.assert_called()
    
    def test_remove_handler(self):
        mock1 = unittest.mock.Mock()
        mock2 = unittest.mock.Mock()
        c1 = Chord(Note(20), Note(40), Note(60))
        c2 = Chord(Note(30), Note(40), Note(50))
        self.CEL.add_chord_handler(mock1, c1)
        self.CEL.add_chord_handler(mock2, c2)

        self.CEL.clear_handlers(c2)

        press_chord(self.loopback, c1)
        time.sleep(TEST_CHORD_DELAY)
        mock1.assert_called()

        press_chord(self.loopback, c2)
        time.sleep(TEST_CHORD_DELAY)
        mock2.assert_not_called()


class test_ChordEventLoop_rtmidi(unittest.TestCase, ChordEventLoop_base_tests):
    def setUp(self):
        self.loopback = LoopbackPort()
        mido.set_backend("mido.backends.rtmidi", load=True)
        self.CEL = ChordEventLoop(port=self.loopback)
    
    def test_warn_on_callbacks_enabled(self):
        with self.assertLogs(logger=logger, level="WARNING"):
            self.CEL.start()


class test_ChordEventLoop_pygame(unittest.TestCase, ChordEventLoop_base_tests):
    def setUp(self):
        self.loopback = LoopbackPort()
        mido.set_backend("mido.backends.pygame", load=True)
        self.CEL = ChordEventLoop(port=self.loopback)
        self.CEL.start()

    def tearDown(self):
        self.CEL.stop()
