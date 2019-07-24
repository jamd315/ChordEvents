import json
import os
import sys
import threading
import queue
from collections import namedtuple

import mido

name = "ChordEvents"  # For PyPi


class Note:
    """Represents a single note.

    Can be created using keywords or implicitly.  1 string argument is mapped to ``note_str``, 1 str and 1 int arguments are mapped to ``note`` and ``octave``, 1 int argument is mapped to ``midi``.

    Attributes:
        note: The note letter, e.g. 'A' or 'F#'
        pc: Pitch class, see https://en.wikipedia.org/wiki/Pitch_class#Integer_notation
        octave: Octave number for the note
        midi: MIDI note number
        freq: Frequency of the note in Hz, might be broken
    
    Args:
        note_str: String with ASCII representation of note.  Can use sharp(#) and flat(b) accidentals.  e.g. Note("A4"), Note("C#2")  Can't be used with any other argument
        note (str): See ``note`` attribute, must be used with ``octave`` argument
        octave (int): See ``octave`` attribute, must be used with ``note`` argument
        midi (int): See ``midi`` attribute.  Can't be used with any other argument.
    """
    pitch_class_map = {  # Overflow is where octave changes
        0: 'C',
        1: 'C#',
        2: 'D',
        3: 'D#',
        4: 'E',
        5: 'F',
        6: 'F#',
        7: 'G',
        8: 'G#',
        9: 'A',
        10: 'A#',
        11: 'B'
    }
    pitch_class_map_complement = {j: i for i, j in pitch_class_map.items()}

    def __init__(self, *args, note_str=None, note=None, octave=None, midi=None):
        # Constructor pre-processing sets the same variables as passed to __init__ to let logic below finalize construction

        # Implicit argument mapping
        if len(args) == 1 and isinstance(args[0], str):
            note_str = args[0]
        elif len(args) == 1 and isinstance(args[0], int):
            midi = args[0]
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], int):
            note = args[0]
            octave = args[1]
        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], str):  # Probably won't actually happen, Note(4, "A")
            octave = args[0]
            note = args[1]
        
        if note_str and any(x is not None for x in [note, octave, midi]):
            raise TypeError("Passing both keyword arguments for note/octave/midi is not supported while using positional argument note_str")
        
        if note_str:  # Only supports single digit octave TODO
            note = note_str[:-1]
            try:
                octave = int(note_str[-1])
            except ValueError:
                raise ValueError("Missing octave number in note_str, note_str should end with the octave number.")

        if note is not None and octave is not None:  # From note and octave
            if len(note) == 2 and note[-1] == "b":  # Flat, convert to sharp
                pc = self.pitch_class_map_complement[note[0]] - 1  # Decrement pitch class
                if pc == -1:  # Underflow
                    note = "B"
                    octave -= 1
                else:
                    note = self.pitch_class_map[pc]
            self.note = note
            self.octave = octave
            self.midi = self._note_octave_to_midi(note, octave)
        elif midi is not None:  # From MIDI
            self.note, self.octave = self._midi_to_note_octave(midi)
            self.midi = midi
        else:
            raise TypeError
        self.pc = self.pitch_class_map_complement[self.note]
        self.freq = 27.5 * 2 ** ((self.midi-21)/21)  # In Hz  TODO could be broken

    def __str__(self):
        return self.note + str(self.octave)
    
    def __repr__(self):
        return "Note(" + str(self) + ")"

    def __gt__(self, other):
        return self.midi > other.midi
    
    def __eq__(self, other):
        return self.midi == other.midi


    @classmethod
    def _note_octave_to_midi(cls, note, octave):
        """For use with the pitch_class_map class attribute"""
        assert isinstance(note, str)
        assert isinstance(octave, int)
        pc = cls.pitch_class_map_complement[note]
        midi = octave * 12 + pc + 12
        return midi

    @classmethod
    def _midi_to_note_octave(cls, m):
        """For use with the pitch_class_map class attribute"""
        assert isinstance(m, int)
        m -= 12  # C0 is midi 12
        octave, note = divmod(m, 12)
        note = cls.pitch_class_map[note]
        return (note, octave)


class Chord:
    """Contains Note objects, as well as functions to analyze chords.  Accepts either a single list/tuple of notes, or a bunch of notes.  Typically contructed using ``from_ascii()`` or ``from_midi_list()``.

    Attributes:
        notes: List of ``Note`` objects

    Args:
        args: List of ``Note`` objects or multiple ``Note`` objects passed to constructor.
    """
    with open(os.path.join(os.path.split(__file__)[0], "chords.json"), "r") as f:
        chords = json.load(f)["chords"]
        
    def __init__(self, *args):
        self.notes = self._parse_note_args(args)
        self.notes = sorted(self.notes)

    def __repr__(self):
        return "Chord(" + ", ".join(str(x) for x in self.notes) + ")"

    def __str__(self):
        return repr(self)
    
    def __eq__(self, other):
        if len(self.notes) != len(other.notes):
            return False
        return all(x == y for x, y in zip(self.notes, other.notes))

    def identify(self):
        """Identify what chord this is.  Most chords from this list are valid.  https://en.wikipedia.org/wiki/List_of_chords
        
        Return:
            Name of chord in format "note_ascii chord_name", e.g. "C4 Major"
        """
        try:
            base = str(self.notes[0])
        except IndexError:
            return
        my_semitones = self._get_semitones()
        out = []
        for chord in self.chords:
            for chord_semitones in chord["semitones"]:
                if my_semitones == chord_semitones:
                    out.append(base + " " + chord["name"])
        return out

    def _get_semitones(self):
        semitones = []
        for note in self.notes:
            semitones.append(note.midi - self.notes[0].midi)
        return semitones

    @classmethod
    def from_ascii(cls, note_string):
        """Used to create a ``Chord`` from a string of notes.
        
        Args:
            note_string: Space or comma-space separated ASCII notes
        """
        note_string = note_string.replace(",", "")
        return cls([Note(x) for x in note_string.split(" ")])
    
    @classmethod
    def from_ident(cls, ident_chord_name):
        """Used to create a ``Chord`` from an identified chord, e.g. 'C4 Major.  Wraps ``from_note_chord()``'

        Args:
            ident_chord_name: Chord name similar to what ``Chord.identify`` outputs.
        """
        base_note, *chord_name = ident_chord_name.split(" ")
        base_note = Note(base_note)
        chord_name = " ".join(chord_name).strip()
        return cls.from_note_chord(base_note, chord_name)
        
    @classmethod
    def from_note_chord(cls, note_obj, chord_name):
        """Used to create a ``Chord`` from a ``Note`` and a chord name

        Args:
            note_obj: ``Note`` object representing the base note of the chord
            chord_name: String name of chord, see names of chord in chords.json.  e.g. "Major", or "Harmonic seventh"
        """
        note_list = [Note(note_obj.midi + semitone) for semitone in cls._get_semitones_from_chord_name(chord_name)]
        return cls(note_list)

    @classmethod
    def from_midi_list(cls, midi_list):
        """Used to create a ``Chord`` from a list of MIDI codes
        
        Args:
            midi_list: List of integers represnting MIDI note codes"""
        return cls([Note(x) for x in midi_list])

    @classmethod
    def _get_semitones_from_chord_name(cls, chord_name):
        """Return a the 1st semitone from the list of semitones in chords.json for a given chord name"""
        for chord in cls.chords:
            if chord_name == chord["name"]:
                return chord["semitones"][0]
        raise ValueError("Chord not found, see https://en.wikipedia.org/wiki/List_of_chords")

    @staticmethod
    def _parse_note_args(note_args):
        """Process args tuple into nice Note() list"""
        assert isinstance(note_args, tuple)  # Needs to be passed the args tuple
        try:
            if all(type(x) == Note for x in note_args):
                return note_args
            elif all(type(x) == Note for x in note_args[0]):
                return note_args[0]
            else:
                raise ValueError("Illegal configuration of notes")
        except TypeError:
            raise TypeError("Expected iterable of Notes")


class ChordEventLoop:
    """The event loop that watches for chords and calls the event handlers
    
    Args:
        port: ``mido`` port.  Default is "default", which gets the 1st port from ``mido.get_input_names()``
        verbose:  Boolean used to control whether to print a bunch of extra stuff
    
    Attributes:
        down_notes: ``set()`` of down notes
        handlers: list of handlers, see ``ChordEventLoop.EventHandler``
        port: mido port being used
    
    TODO:
        Need a way to remove specific event handlers
    """

    EventHandler = namedtuple("EventHandler", ["chord_obj", "func"])
    """Used to represent an event handler."""

    def __init__(self, port="default", verbose=False):
        self.handlers = []
        self.down_notes = set()
        if port == "default":
            self.port = mido.open_input(mido.get_input_names()[0])
        elif isinstance(port, mido.ports.BasePort):
            self.port = port
        elif isinstance(port, str):
            self.port = mido.open_input(port)
        else:
            raise ValueError("Expected mido port or string name compatible with ``mido.open_input()``")
        self._verbose = verbose
        self._running = False
        self._thread = None
        mido.set_backend("mido.backends.pygame")  # TODO config this

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
        if self._verbose:
            print("Added handler for chord " + str(chord_obj))
        self.handlers.append(self.EventHandler(chord_obj, func))
    
    def clear_handlers(self):
        """Clear all chord handlers"""
        self.handlers = []

    def start(self, blocking=False):
        """Start the main loop, required to process MIDI and trigger event handlers.  Loop can be stopped with ``stop()``.
        
        Args:
            blocking: Default False.  Determines if this call will be blocking, requiring the ``stop()`` function to be called from an event handler."""
        self._running = True
        self._thread = threading.Thread(target=self._loop)
        self._thread.start()
        if blocking:
            self._thread.join()

    def stop(self):
        """Stop the main loop.  Loop can be restarted with ``start()`` after being stopped."""
        self._running = False
        self._thread.join()
        self._thread = None

    def _loop(self):  # TODO probably rewrite this whole tree
        with self.port as inport:
            while self._running:
                for msg in inport.iter_pending():
                    if msg.type == "note_on":
                        if msg.velocity > 0:  # Down
                            self.down_notes.add(msg.note)
                            my_chord = Chord.from_midi_list(self.down_notes)
                            identified = my_chord.identify()  # Only scans on key down to save CPU use
                            if identified:
                                for ident in identified:
                                    for h in self.handlers:
                                        if ident == h.chord_obj:
                                            self._start_handler(h)
                                if self._verbose:
                                    print(", ".join(identified))
                            else:
                                for h in self.handlers:
                                    if isinstance(h.chord_obj, Chord) and h.chord_obj == my_chord:
                                        self._start_handler(h)
                        else:  # Up
                            self.down_notes.remove(msg.note)
                    elif msg.type == "note_off":  # Up
                        self.down_notes.remove(msg.note)
            if self._verbose:
                print("Loop exit")

    def _start_handler(self, handler):
        if self._verbose:
            print("Triggered handler for chord " + str(handler.chord_obj))
        t = threading.Thread(target=handler.func)
        t.daemon = True
        t.start()


class LoopbackInput(mido.ports.BaseInput):
    """Used for testing"""
    def __init__(self, *args, **kwargs):
        try:
            if kwargs["verbose"]:
                self.verbose = True
        except KeyError:
            self.verbose = False
        super().__init__()
    
    def _open(self, **kwargs):
        self._my_queue = queue.Queue()
        if self.verbose:
            print("Opened loopback port")
    
    def _close(self, **kwargs):
        self._my_queue = queue.Queue()  # Clear it with a new queue
        if self.verbose:
            print("Closed loopback port")

    def _receive(self, block=True):
        if block:
            return self._my_queue.get()
        else:
            try:
                return self._my_queue.get(block=False)
            except queue.Empty:
                return
    
    def create_msg(self, msg):
        """Sends a MIDI message to the port to be echoed to the """
        self._my_queue.put(msg)


def main():
    m = ChordEventLoop()
    m.start()
    input("Press enter to stop\n")
    m.stop()


if __name__ == "__main__":
    main()
