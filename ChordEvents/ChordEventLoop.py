import logging
import os
import threading
from collections import namedtuple

import mido

import ChordEvents
from ChordEvents import Chord, Note

logger = logging.getLogger(__name__)


class ChordEventLoop:
    """The event loop that watches for chords and calls the event handlers.  Uses callbacks if the backend supports it.  Otherwise an internal loop will need to be started with ``start()`` and ``stop()``.
    
    Args:
        port: ``mido`` port.  Default is "default", which gets the 1st port from ``mido.get_input_names()``.  Also accepts strings as returned form ``mido.get_input_names()``.
    
    Attributes:
        down_notes: ``set`` of down notes
        handlers: ``dict`` of chords mapped to a list of of handlers
        port: mido port being used
    """

    def __init__(self, port="default"):
        self.handlers = dict()
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
        if ChordEvents.callbacks_supported():
            self.port.callback = self._callback
        else:
            self._running = False
            self._thread = None
        logger.debug("Created new ChordEventLoop with __init__")
    
    def __del__(self):
        if not ChordEvents.callbacks_supported():
            self.stop()
        if hasattr(self, "port") and isinstance(self.port, mido.ports.BasePort):
            self.port.close()

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
        chord_obj = self._resolve_chord_obj(chord_obj)
        try:
            self.handlers[chord_obj] += func
        except KeyError:
            self.handlers[chord_obj] = [func]
        logger.debug("Added handler for chord {}".format(chord_obj))
    
    def clear_handlers(self, chord_obj=None):
        """Clear handlers for a given ``chord_obj``.  Default is to clear all handlers if ``chord_obj`` is not specified.
        
        Args:
            chord_obj: Chord name as string, as output from ``Chord.identify()``, or ``Chord`` object"""
        if chord_obj is not None:
            chord_obj = self._resolve_chord_obj(chord_obj)
            try:
                del self.handlers[chord_obj]
                logger.debug("Cleared handlers for {}".format(chord_obj))
            except KeyError:
                pass
        else:
            self.handlers = dict()
            logger.info("Cleared all handlers")

    def start(self, blocking=False):
        """Only required when backend doesn't support callbacks.  Start the main loop, required to process MIDI and trigger event handlers.  Loop can be stopped with ``stop()``.
        
        Args:
            blocking: Default False.  Determines if this call will be blocking, requiring the ``stop()`` function to be called from an event handler.
        """
        if not ChordEvents.callbacks_supported():
            self._running = True
            self._thread = threading.Thread(target=self._loop, name="ChordEventLoop thread")
            self._thread.start()
            logger.info("ChordEventLoop thread started")
            if blocking:
                self._thread.join()
        else:
            logger.warn("Called start() while using a backend that supports callbacks.")

    def stop(self):
        """Only required when backend doesn't support callbacks.  Stop the main loop.  Loop can be restarted with ``start()`` after being stopped."""
        if not ChordEvents.callbacks_supported():
            self._running = False
            try:
                self._thread.join()
            except AttributeError:  # Already garbage collected
                pass
            self._thread = None
            logger.info("ChordEventLoop thread stopped")
        else:
            logger.warn("Called stop() while using a backend that supports callbacks.")

    def _loop(self):
        while self._running:
            for msg in self.port.iter_pending():
                self._callback(msg)

    def _callback(self, msg):
        if msg.type == "note_on" and msg.velocity > 0:  # Key down
            self.down_notes.add(msg.note)
            self._check_handlers()
            logger.debug("Note on")
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):  # Key up
            self.down_notes.remove(msg.note)
            logger.debug("Note off")
    
    def _check_handlers(self):
        test_chord = Chord.from_midi_list(self.down_notes)
        try:
            for func in self.handlers[test_chord]:
                logger.debug("Triggered handler for chord {}".format(test_chord))
                t = threading.Thread(target=func)
                t.daemon = True
                t.start()
        except KeyError:
            pass
    
    @staticmethod
    def _resolve_chord_obj(chord_obj):
        if isinstance(chord_obj, Chord):
            return chord_obj
        elif isinstance(chord_obj, str):
            return Chord.from_ident(chord_obj)
        else:
            raise TypeError("Expected string chord name or Chord")
