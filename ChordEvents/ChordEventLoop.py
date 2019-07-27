import logging
import os
import threading
from collections import namedtuple

import mido

from ChordEvents import Note, Chord

logger = logging.getLogger(__name__)


class ChordEventLoop:
    """The event loop that watches for chords and calls the event handlers
    
    Args:
        port: ``mido`` port.  Default is "default", which gets the 1st port from ``mido.get_input_names()``
    
    Attributes:
        down_notes: ``set()`` of down notes
        handlers: list of handlers, see ``ChordEventLoop.EventHandler``
        port: mido port being used
    
    TODO:
        Need a way to remove specific event handlers
    """

    EventHandler = namedtuple("EventHandler", ["chord_obj", "func"])
    """Used to represent an event handler."""

    def __init__(self, port="default"):
        self.handlers = []
        self.down_notes = set()
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
            raise ValueError("Expected mido port or string name compatible with ``mido.open_input()``")
        self._running = False
        self._thread = None
        logger.debug("Created new ChordEventLoop with __init__")
    
    def __del__(self):
        if self._running:
            logger.warning("__del__ used on a running loop, please stop() the ChordEventLoop before closing")
            self.stop()

    def on_chord(self, chord_obj):
        """Decorator function similar to ``add_chord_handler``"""
        def _on_chord_sub(func):
            self.add_chord_handler(func, chord_obj)
            return func
        return _on_chord_sub

    def add_chord_handler(self, func, chord_obj):
        """Create a new event handler that runs the function when a chord is pressed
        
        Args:
            chord_obj: Chord name as string, as output from ``Chord.identify()``, or ``Chord`` object
            func: Function to call when the chord is detected.  Will be spawned in a new daemon thread.
        """
        logger.info("Added handler for chord {}".format(chord_obj))
        self.handlers.append(self.EventHandler(chord_obj, func))
    
    def clear_handlers(self):
        """Clear all chord handlers"""
        logger.info("Cleared handlers")
        self.handlers = []

    def start(self, blocking=False):
        """Start the main loop, required to process MIDI and trigger event handlers.  Loop can be stopped with ``stop()``.
        
        Args:
            blocking: Default False.  Determines if this call will be blocking, requiring the ``stop()`` function to be called from an event handler."""
        self._running = True
        self._thread = threading.Thread(target=self._loop, name="ChordEventLoop internal thread")
        self._thread.start()
        logger.info("ChordEventLoop started")
        if blocking:
            self._thread.join()

    def stop(self):
        """Stop the main loop.  Loop can be restarted with ``start()`` after being stopped."""
        self._running = False
        try:
            self._thread.join()
        except AttributeError:  # Already garbage collected
            pass
        self._thread = None
        logger.info("ChordEventLoop stopped")

    def _loop(self):  # This is only necessary because pygame doesn't support callbacks.  TODO consider using rtmidi?
        with self.port as inport:
            while self._running:
                for msg in inport.iter_pending():
                    self._mido_callback(msg)

    def _mido_callback(self, msg):
        if msg.type == "note_on" and msg.velocity > 0:  # Key down
            self.down_notes.add(msg.note)
            self._check_handlers()
            logger.debug("Note on")
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):  # Key up
            self.down_notes.remove(msg.note)
            logger.debug("Note off")
    
    def _check_handlers(self):
        test_chord = Chord.from_midi_list(self.down_notes)
        identified = test_chord.identify()
        for handler in self.handlers:
            if handler.chord_obj == test_chord or handler.chord_obj in identified:
                logger.info("Triggered handler for chord {}".format(handler.chord_obj))
                t = threading.Thread(target=handler.func)
                t.daemon = True
                t.start()
