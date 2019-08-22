import collections
import json
import logging
import os

from MIDIEvents import Note, NoteList

logger = logging.getLogger("MIDIEvents")


class Chord(NoteList):
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
        base_note, *chord_name = ident_chord_name.split(" ")
        assert chord_name, "No chord name detected, make sure there's a space in ident_chord_name."
        base_note = Note(base_note)
        chord_name = " ".join(chord_name).strip()
        return cls.from_note_chord(base_note, chord_name)

    @classmethod
    def from_note_chord(cls, note_obj, chord_name):
        note_list = [Note(note_obj.midi + semitone) for semitone in cls._get_semitones_from_chord_name(chord_name)]
        return cls(note_list)

    @classmethod
    def _get_semitones_from_chord_name(cls, chord_name):
        for chord in cls.chords:
            if chord_name == chord["name"]:
                return chord["semitones"][0]
        raise ValueError("Chord not found, see https://en.wikipedia.org/wiki/List_of_chords")
