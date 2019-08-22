import logging
import threading
from collections import deque

import mido

import MIDIEvents
from MIDIEvents import Chord, Sequence

logger = logging.getLogger("MIDIEvents")


class MIDIEventLoop:
    def __init__(self, port="default"):
        self.running_handler_threads = list()
        self.chord_handlers = dict()
        self.sequence_handlers = dict()
        self.down_notes = set()
        self.recent_notes = deque(maxlen=Sequence.maxlen)
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

        if isinstance(notes_obj, Sequence):
            if notes_obj in self.sequence_handlers:
                self.sequence_handlers[notes_obj].append(func)
            else:
                self.sequence_handlers[notes_obj] = [func]

        if isinstance(notes_obj, Chord):
            if notes_obj in self.chord_handlers:
                self.chord_handlers[notes_obj].append(func)  # Append callback to handler list
            else:
                self.chord_handlers[notes_obj] = [func]  # Create handler list for notes_obj with callback

        logger.debug(f"Added handler for {notes_obj}")

    def clear_handlers(self, notes_obj=None):
        if notes_obj is not None:
            notes_obj = self._resolve_notes_obj(notes_obj)
            if notes_obj in self.chord_handlers:
                del self.chord_handlers[notes_obj]
                logger.debug(f"Cleared chord_handlers for {notes_obj}")
            if notes_obj in self.sequence_handlers:
                del self.sequence_handlers[notes_obj]
                logger.debug(f"Cleared sequence_handlers for {notes_obj}")
        else:
            self.chord_handlers = dict()
            self.sequence_handlers = dict()
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
            self._check_handlers()
            logger.debug(f"Note {msg.note} on")
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):  # Key up
            self.down_notes.remove(msg.note)
            logger.debug(f"Note {msg.note} off")
    
    def _check_handlers(self):
        """Search for handlers to trigger in self.chord_handlers and self.recent_notes (Sequence)"""

        # Find the Chords.  Uses __hash__ to find them in a dictionary.
        test_chord = Chord.from_midi_list(self.down_notes)
        if test_chord in self.chord_handlers:
            for func in self.chord_handlers[test_chord]:
                logger.debug(f"Triggered handler for {test_chord}")
                self._execute_handler(func)

        # Find the Sequences.  Uses __eq__ to iterate over the sequence handlers and compare to recent notes.
        # TODO investigate another way to do this that might be faster
        for seq, func_list in self.sequence_handlers.items():
            if seq == self.recent_notes:
                for func in func_list:
                    logger.debug(f"Triggered handler for {seq}")
                    self._execute_handler(func)

    @staticmethod
    def _resolve_notes_obj(notes_obj):
        if isinstance(notes_obj, str):
            notes_obj = Chord.from_ident(notes_obj)
        assert isinstance(notes_obj, Chord) or isinstance(notes_obj, Sequence), "Expected a Sequence or Chord"  # Just to make sure
        return notes_obj
    
    def _execute_handler(self, func):
        t = threading.Thread(target=func)
        t.daemon = True
        t.start()
        self.running_handler_threads.append(t)
