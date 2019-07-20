import json
import os
import sys
import threading
from collections import namedtuple

import mido


class Note:
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
        self.note = note  # Note character, eg 'A' or 'F'
        self.pc = self.pitch_class_map_complement[note]  # Pitch class https://en.wikipedia.org/wiki/Pitch_class#Integer_notation
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
        """Accepts MIDI note number"""
        note, octave = cls._midi_to_note_octave(m)
        return cls(note, octave, m)

    @classmethod
    def from_note_octave(cls, note, octave):
        """Accepts note (note character) and octave"""
        midi = cls._note_octave_to_midi(note, octave)
        return cls(note, octave, midi)

    @classmethod
    def from_ascii(cls, string):
        """Accepts the str representation of a note, e.g. A0, C#4, Bb6"""
        note = string[:-1]
        octave = int(string[-1])
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

    _folder_context = os.path.split(__file__)[0]
    with open(os.path.join(_folder_context, "chords.json"), "r") as f:
        chords = json.load(f)["chords"]

    def __init__(self, *args):
        """Accepts either a list/tuple of notes, or a bunch of notes"""
        self.notes = self._parse_note_args(args)
        self.notes = sorted(self.notes)

    def __repr__(self):
        return "Chord(" + ", ".join(str(x) for x in self.notes) + ")"

    def __str__(self):
        return repr(self)

    def identify(self):
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
        """Space or comma-space separated list of notes"""
        note_string = note_string.replace(",", "")
        return cls([Note.from_ascii(x) for x in note_string.split(" ")])

    @classmethod
    def from_midi_list(cls, midi_list):
        """List of integer midi note codes"""
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
    EventHandler = namedtuple("EventHandler", ["chord_name", "func"])

    def __init__(self, verbose=False):
        self.handlers = []
        self._verbose = verbose
        self._running = False
        self._thread = None
        if sys.platform == "win32":
            mido.set_backend("mido.backends.pygame")  # Was easier to set up on windows
        elif sys.platform == "linux":
            mido.set_backend("mido.backends.rtmidi")  # Technically this is default

    def on_chord(self, chord_name, func):
        self.handlers.append(self.EventHandler(chord_name, func))

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop)
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join()

    def _loop(self):
        down_notes = set()
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
