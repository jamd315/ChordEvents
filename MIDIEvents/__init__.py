import logging

import mido

from MIDIEvents.LoopbackPort import LoopbackPort
# This order matters
from MIDIEvents.Note import Note
from MIDIEvents.NoteList import NoteList
from MIDIEvents.Chord import Chord
from MIDIEvents.Sequence import Sequence
from MIDIEvents.MIDIEventLoop import MIDIEventLoop

__all__ = [
    "Note",
    "NoteList",
    "Chord",
    "Sequence",
    "MIDIEventLoop",
    "LoopbackPort"
]


def callbacks_supported():
    return mido.backend.name in ["mido.backends.rtmidi", "mido.backends.rtmidi_python"]


logger = logging.getLogger("MIDIEvents")
mido.set_backend()  # environment var MIDO_BACKEND or default.  Unloaded
logger.debug(f"Using backend '{mido.backend.name}' from either default or environment variable.  Backend {'supports' if callbacks_supported() else 'does not support'} callbacks.")
