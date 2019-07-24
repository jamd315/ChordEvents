import time
import mido
import queue
import unittest
import unittest.mock

from ChordEvents import LoopbackInput, ChordEventLoop, Chord, Note

flag = False

def toggle_flag():
    global flag
    flag = not flag
    print("\n\n\nToggled\n\n\n")


class test_ChordEventLoop(unittest.TestCase):
    def setUp(self):
        self.loopback = LoopbackInput()
        self.CEL = ChordEventLoop(port=self.loopback)
        self.CEL.start()
        self.flag = False

    def tearDown(self):
        self.CEL.stop()
    
    def test_handlers_add_remove(self):
        mock = unittest.mock.Mock()
        self.assertFalse(self.CEL.handlers)  # Empty
        self.CEL.add_chord_handler(mock, "C4 Major")
        self.assertTrue(self.CEL.handlers)  # Not empty
        self.CEL.clear_handlers()
        self.assertFalse(self.CEL.handlers)

    def test_note_on(self):
        """Test that a chord is detected and that the notes are released when a 0 velocity ``note_on`` message type is received"""
        mock = unittest.mock.Mock()
        self.CEL.add_chord_handler(mock, "C4 Major")  # Decorate

        self.loopback.create_msg(mido.Message("note_on", note=60))  # C4
        self.loopback.create_msg(mido.Message("note_on", note=64))  # E4
        self.loopback.create_msg(mido.Message("note_on", note=67))  # G4
        
        self.loopback.create_msg(mido.Message("note_on", note=60, velocity=0))
        self.loopback.create_msg(mido.Message("note_on", note=64, velocity=0))
        self.loopback.create_msg(mido.Message("note_on", note=67, velocity=0))
        

        time.sleep(0.01)  # 10x the default polling speed
        self.assertFalse(self.CEL.down_notes)  # assert empty
        mock.assert_called()
        self.CEL.clear_handlers()


    def test_note_off(self):
        """Test that a chord is detected and that the notes are release when the ``note_off`` message type is received"""
        mock = unittest.mock.Mock()
        self.CEL.add_chord_handler(mock, "C4 Major")  # Decorate

        self.loopback.create_msg(mido.Message("note_on", note=60))  # C4
        self.loopback.create_msg(mido.Message("note_on", note=64))  # E4
        self.loopback.create_msg(mido.Message("note_on", note=67))  # G4
        
        self.loopback.create_msg(mido.Message("note_off", note=60))
        self.loopback.create_msg(mido.Message("note_off", note=64))
        self.loopback.create_msg(mido.Message("note_off", note=67))
        

        time.sleep(0.01)
        self.assertFalse(self.CEL.down_notes)  # assert empty
        mock.assert_called()
        self.CEL.clear_handlers()

    def test_trigger_on_custom_chord(self):
        mock = unittest.mock.Mock()
        chord = Chord.from_midi_list([20, 40, 60])
        self.assertFalse(self.CEL.handlers)  # Empty check
        self.CEL.add_chord_handler(mock, chord)

        self.loopback.create_msg(mido.Message("note_on", note=20))
        self.loopback.create_msg(mido.Message("note_on", note=40))
        self.loopback.create_msg(mido.Message("note_on", note=60))

        self.loopback.create_msg(mido.Message("note_off", note=20))
        self.loopback.create_msg(mido.Message("note_off", note=40))
        self.loopback.create_msg(mido.Message("note_off", note=60))
    
        time.sleep(0.01)
        mock.assert_called()
        self.CEL.clear_handlers()