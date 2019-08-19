import collections
import json
import logging
import os

from MIDIEvents import Note, NoteList

logger = logging.getLogger("MIDIEvents")


class Chord(NoteList):
    """Contains Note objects, as well as functions to analyze chords.
    Accepts either a single iterable notes, or a bunch of notes.
    Typically constructed using ``from_ascii()`` or ``from_midi_list()``.
    """
    with open(os.path.join(os.path.split(__file__)[0], "chords.json"), "r") as f:
        chords = json.load(f)["chords"]

    def __init__(self, *args):
        super().__init__(args)

    def __eq__(self, other):
        if isinstance(other, self.__class__) or issubclass(self.__class__, other.__class__):
            if len(self.notes) != len(other.notes):
                return False
            return collections.Counter(self.notes) == collections.Counter(other.notes)
        return False

    __hash__ = NoteList.__hash__

    def identify(self):
        """Identify what chord this is.  Most chords here are valid.  https://en.wikipedia.org/wiki/List_of_chords
        
        Return:
            List of chord names in format "note_ascii chord_name", e.g. "C4 Major"
        """
        if len(self.notes) == 0:
            return
        base = str(self.notes[0])
        my_semitones = self._get_semitones()
        out = []
        for chord in self.chords:
            for chord_semitones in chord["semitones"]:
                if my_semitones == chord_semitones:
                    out.append(base + " " + chord["name"])
        logger.debug("identify found {} chords".format(len(out)))
        return out

    def _get_semitones(self):
        semitones = []
        for note in self.notes:
            semitones.append(note.midi - self.notes[0].midi)
        return semitones

    @classmethod
    def from_ident(cls, ident_chord_name):
        """Used to create a ``Chord`` from an identified chord, e.g. 'C4 Major.  Wraps ``from_note_chord()``'

        Args:
            ident_chord_name: Chord name similar to what ``Chord.identify`` outputs.
        """
        base_note, *chord_name = ident_chord_name.split(" ")
        assert chord_name, "No chord name detected, make sure there's a space in ident_chord_name."
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
    def _get_semitones_from_chord_name(cls, chord_name):
        """Return the 1st semitone from the list of semitones in chords.json for a given ``chord_name``"""
        for chord in cls.chords:
            if chord_name == chord["name"]:
                return chord["semitones"][0]
        raise ValueError("Chord not found, see https://en.wikipedia.org/wiki/List_of_chords")
