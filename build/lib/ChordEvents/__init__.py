import json
import os
import sys
import threading
from collections import namedtuple

import mido

name = "ChordEvents"  # For PyPi


class Note:
    """Represents a single note.

    Typically created using ``from_midi()``, ``from_note_octave()``, or ``from_ascii()``, but can also be created if you already know the note, it's octave, and the midi number for the note.

    Attributes:
        note: The note letter, e.g. 'A' or 'F'
        pc: Pitch class, see https://en.wikipedia.org/wiki/Pitch_class#Integer_notation
        octave: Octave number for the note
        midi: MIDI note number
        freq: Frequency of the note in Hz
    
    Args:
        note (str): See ``note`` attribute
        octave (int): See ``octave`` attribute
        midi (int): See ``midi`` attribute
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

    def __init__(self, note, octave, midi):
        self.note = note
        self.pc = self.pitch_class_map_complement[note]
        self.octave = octave
        self.midi = midi
        self.freq = 27.5 * 2 ** ((self.midi-21)/21)  # In Hz

    def __str__(self):
        return self.note + str(self.octave)
    
    def __repr__(self):
        return "Note(" + str(self) + ")"

    def __gt__(self, other):
        return self.midi > other.midi

    @classmethod
    def from_midi(cls, m):
        """Used to create a new ``Note`` object when you only have the MIDI number

        Args:
            m: See ``midi`` attribute
        """
        note, octave = cls._midi_to_note_octave(m)
        return cls(note, octave, m)

    @classmethod
    def from_note_octave(cls, note, octave):
        """Used to create a new ``Note`` object when you don't know the MIDI number
        
        Args:
            note: See ``note`` attribute
            octave: See ``octave attribute``
        """
        midi = cls._note_octave_to_midi(note, octave)
        return cls(note, octave, midi)

    @classmethod
    def from_ascii(cls, note_ascii):
        """Used to create a new ``Note`` object with an ASCII representation of the note, e.g. A0, C#3, or Bb4
        
        Args:
            note_ascii: string with ASCII representation of note
        """
        note = note_ascii[:-1]
        octave = int(note_ascii[-1])
        if note[-1] == "b":  # Flat, convert to sharp
            pc = cls.pitch_class_map_complement[note[0]] - 1
            if pc == -1:  # Underflow
                note = "B"
                octave -= 1
            else:
                note = cls.pitch_class_map[pc]
        return cls.from_note_octave(note, octave)

    @classmethod
    def _note_octave_to_midi(cls, note, octave):
        """For use with the pitch_class_map class attribute"""
        pc = cls.pitch_class_map_complement[note]
        midi = octave * 12 + pc + 12
        return midi

    @classmethod
    def _midi_to_note_octave(cls, m):
        """For use with the pitch_class_map class attribute"""
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
            note_string: Space or comma-space separated ASCII notes"""
        note_string = note_string.replace(",", "")
        return cls([Note.from_ascii(x) for x in note_string.split(" ")])

    @classmethod
    def from_midi_list(cls, midi_list):
        """Used to create a ``Chord`` from a list of MIDI codes
        
        Args:
            midi_list: List of integers represnting MIDI note codes"""
        return cls([Note.from_midi(x) for x in midi_list])

    @staticmethod
    def _parse_note_args(note_args):
        """Process args into nice Note() list"""
        if all(type(x) == Note for x in note_args):
            return note_args
        elif all(type(x) == Note for x in note_args[0]):
            return note_args[0]
        else:
            raise ValueError("Illegal configuration of notes")


class ChordEventLoop:
    """The event loop that watches for chords and calls the event handlers
    
    Args:
        verbose:  Boolean used to control whether to print a bunch of extra stuff
    
    TODO:
        Need a way to remove specific event handlers
    """
    EventHandler = namedtuple("EventHandler", ["chord_name", "func"])
    """Used to represent an event handler."""
    def __init__(self, verbose=False):
        self.handlers = []
        self._verbose = verbose
        self._running = False
        self._thread = None
        if sys.platform == "win32":
            mido.set_backend("mido.backends.pygame")  # Was easier to set up on windows
        elif sys.platform == "linux":
            mido.set_backend("mido.backends.rtmidi")  # Technically this is default

    def on_chord(self, chord_name):
        """Decorator function similar to ``add_chord_handler``"""
        def _on_chord_sub(func):
            self.add_chord_handler(func, chord_name)
            return func
        return _on_chord_sub

    def add_chord_handler(self, func, chord_name):
        """Create a new event handler that runs the function when a chord is pressed
        
        Args:
            chord_name: Chord name, as output from ``Chord.identify()``
            func: Function to call when the chord is detected.  Will be spawned in a new daemon thread.
        """
        self.handlers.append(self.EventHandler(chord_name, func))
    
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

    def _loop(self):
        down_notes = set()
        try:
            input_name = mido.get_input_names()[0]  # TODO should have a config to manually pick this
        except IndexError:
            raise RuntimeError("Didn't find any MIDI inputs")
        with mido.open_input(mido.get_input_names()[0]) as inport:  # pylint:disable=E1101
            while self._running:
                for msg in inport.iter_pending():
                    if msg.type == "note_on":
                        if msg.velocity > 0:  # Down
                            down_notes.add(msg.note)
                            identified = Chord.from_midi_list(down_notes).identify()  # Only scans on key down to save CPU use
                            if identified:
                                for ident in identified:
                                    for h in self.handlers:
                                        if ident == h.chord_name:
                                            self._start_handler(h.func)
                                if self._verbose:
                                    print(", ".join(identified))
                        else:  # Up
                            down_notes.remove(msg.note)
            if self._verbose:
                print("Loop exit")

    @staticmethod
    def _start_handler(func, *args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()


def main():
    m = ChordEventLoop()
    m.start()
    input("Press enter to stop\n")
    m.stop()


if __name__ == "__main__":
    main()
