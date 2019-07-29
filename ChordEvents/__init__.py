import logging

import mido

import ChordEvents.logger
from ChordEvents.__version__ import __version__
from ChordEvents.LoopbackPort import LoopbackPort
# This order matters
from ChordEvents.Note import Note
from ChordEvents.Chord import Chord
from ChordEvents.ChordEventLoop import ChordEventLoop

__all__ = [
    "Note",
    "Chord",
    "ChordEventLoop",
    "LoopbackPort"
]

def callbacks_supported():
    return mido.backend.name in ["mido.backends.rtmidi", "mido.backends.rtmidi_python"]

logger = logging.getLogger("ChordEvents")
mido.set_backend()  # environment var MIDO_BACKEND or default.  Unloaded
logger.debug("Using backend '{}' from either default or environment variable.  Backend {} callbacks.".format(mido.backend.name, ("supports" if callbacks_supported() else "does not support")))
