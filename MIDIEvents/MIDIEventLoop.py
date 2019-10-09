import logging
import threading
from collections import deque

import mido

import MIDIEvents
from MIDIEvents import Chord, Sequence, ChordProgression

logger = logging.getLogger("MIDIEvents")


class MIDIEventLoop:
    def __init__(self, port="default", check_chords=True, check_sequences=True, check_chord_progressions=True):
        self.check_chords = check_chords  # TODO test these bits
        self.check_sequences = check_sequences
        self.check_chord_progressions = check_chord_progressions
        self.running_handler_threads = list()
        self.handlers = dict()
        self.down_notes = set()
        self.recent_notes = deque(maxlen=Sequence.maxlen)
        self.recent_chords = deque(maxlen=ChordProgression.maxlen)
        if port == "default":
            try:
                self.port = mido.open_input(mido.get_input_names()[0])
            except IndexError:
                raise RuntimeError("No MIDI ports found")
        elif isinstance(port, mido.ports.BasePort):
            self.port = port
        elif isinstance(port, str):
            self.port = mido.open_input(port)
        else:
            raise TypeError("Expected mido port or string name compatible with ``mido.open_input()``")
        if MIDIEvents.callbacks_supported():
            self.port.callback = self._callback
        else:
            self._running = False
            self._thread = None
        logger.debug("Created new MIDIEventLoop with __init__")
    
    def __del__(self):
        if not MIDIEvents.callbacks_supported():
            self.stop()
        if hasattr(self, "port") and isinstance(self.port, mido.ports.BasePort):
            self.port.close()

    def on_notes(self, notes_obj):
        def _sub(func):
            self.add_handler(func, notes_obj)
            return func
        return _sub

    def add_handler(self, func, notes_obj):
        # Pre-process notes_obj
        notes_obj = self._resolve_notes_obj(notes_obj)

        if notes_obj in self.handlers:
            self.handlers[notes_obj].append(func)
        else:
            self.handlers[notes_obj] = [func]
        logger.debug(f"Added handler for {notes_obj}")

    def clear_handlers(self, notes_obj=None):
        if isinstance(notes_obj, type):  # If it's a class remove instances from handlers
            self.handlers = {key: val for key, val in self.handlers.items() if not isinstance(key, notes_obj)}
        elif notes_obj is not None:
            notes_obj = self._resolve_notes_obj(notes_obj)
            del self.handlers[notes_obj]
            logger.debug(f"Cleared handlers for {notes_obj}")
        else:
            self.handlers = dict()
            logger.info("Cleared all handlers")

    def start(self, blocking=False):
        if not MIDIEvents.callbacks_supported():
            self._running = True
            self._thread = threading.Thread(target=self._loop, name="MIDIEventLoop thread")
            self._thread.start()
            logger.info("MIDIEventLoop thread started")
            if blocking:
                self._thread.join()
        else:
            logger.warning("Called start() while using a backend that supports callbacks.")

    def stop(self):
        if not MIDIEvents.callbacks_supported():
            self._running = False
            try:
                self._thread.join()
            except AttributeError:  # Already garbage collected
                pass
            self._thread = None
            logger.info("MIDIEventLoop thread stopped")
        else:
            logger.warning("Called stop() while using a backend that supports callbacks.")

    def _loop(self):
        while self._running:
            for msg in self.port.iter_pending():
                self._callback(msg)

    def _callback(self, msg):
        if msg.type == "note_on" and msg.velocity > 0:  # Key down
            self.recent_notes.append(msg.note)
            self.down_notes.add(msg.note)
            self.recent_chords.append(Chord.from_midi_list(self.down_notes))
            logger.debug(f"Note {msg.note} on")
            self._check_handlers()
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):  # Key up
            self.down_notes.remove(msg.note)
            logger.debug(f"Note {msg.note} off")
    
    def _check_handlers(self):
        """Check the various handlers."""
        if self.check_chords:
            self._check_chord_handlers()
        if self.check_sequences:
            self._check_sequence_handlers()
        if self.check_chord_progressions:
            self._check_chord_progression_handlers()

    def _check_chord_handlers(self):
        """Find the Chords.  Uses __hash__ to find them in a dictionary."""
        test_chord = self.recent_chords[-1]
        if test_chord in self.handlers:
            for func in self.handlers[test_chord]:
                logger.debug(f"Triggered handler for {test_chord}")
                self._execute_handler(func)

    def _check_sequence_handlers(self):
        """
        Find the Sequences.  Uses __eq__ to iterate over the sequence handlers and compare to recent notes.
        TODO investigate another way to do this that might be faster
        """
        for seq, func_list in self.handlers.items():
            if not isinstance(seq, Sequence):
                continue
            if seq == self.recent_notes:
                for func in func_list:
                    logger.debug(f"Triggered handler for {seq}")
                    self._execute_handler(func)

    def _check_chord_progression_handlers(self):
        for c_seq, func_list in self.handlers.items():
            if not isinstance(c_seq, ChordProgression):
                continue
            if c_seq.check_deque(self.recent_chords):
                for func in func_list:
                    logger.debug(f"Triggered handler for {c_seq}")
                    self._execute_handler(func)

    @staticmethod
    def _resolve_notes_obj(notes_obj):
        if isinstance(notes_obj, str):
            notes_obj = Chord.from_ident(notes_obj)
        if not (isinstance(notes_obj, Chord) or isinstance(notes_obj, Sequence) or isinstance(notes_obj, ChordProgression)):
            raise TypeError("Expected a Sequence or Chord")
        return notes_obj
    
    def _execute_handler(self, func):
        t = threading.Thread(target=func)
        t.daemon = True
        t.start()
        self.running_handler_threads.append(t)
