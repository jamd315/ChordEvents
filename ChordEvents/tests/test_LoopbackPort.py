import unittest
import unittest.mock

import mido

from ChordEvents import LoopbackPort


class test_LoopbackPort(unittest.TestCase):
    def setUp(self):
        self.loopback = LoopbackPort()

    def test_callback(self):
        note_on = mido.Message("note_on", note=69)
        mock = unittest.mock.Mock()
        self.loopback.callback = mock
        self.loopback.send(note_on)
        mock.assert_called_with(note_on)
    
    def test_notes_sent_before_callback(self):
        note_on = mido.Message("note_on", note=69)
        mock = unittest.mock.Mock()
        self.loopback.send(note_on)  # Just swap the order on these 2 lines from the previous test
        self.loopback.callback = mock
        mock.assert_called_with(note_on)
    
    def test_baseport_inheritance(self):
        other_loopback = LoopbackPort(name="testing")
        self.assertEqual(other_loopback.name, "testing")
    
    def test_send_receive(self):
        note_on = mido.Message("note_on", note=69)
        self.loopback.send(note_on)
        msg_received = self.loopback.receive(block=False)
        self.assertEqual(note_on, msg_received)
