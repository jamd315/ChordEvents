import json
import logging
import os

from ChordEvents import Note

logger = logging.getLogger("ChordEvents")


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
        if not isinstance(other, Chord):
            return False
        if len(self.notes) != len(other.notes):
            return False
        return all(x == y for x, y in zip(self.notes, other.notes))

    def identify(self):
        """Identify what chord this is.  Most chords from this list are valid.  https://en.wikipedia.org/wiki/List_of_chords
        
        Return:
            List of chord names in format "note_ascii chord_name", e.g. "C4 Major"
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
        try:
            if all(isinstance(x, Note) for x in note_args):
                return note_args
            elif all(isinstance(x, Note) for x in note_args[0]):
                return note_args[0]
            else:
                raise ValueError("Illegal configuration of notes")
        except TypeError:
            raise TypeError("Expected iterable of Notes")
