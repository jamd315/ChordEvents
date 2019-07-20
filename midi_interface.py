import sys
import time
import threading
from collections import namedtuple

import mido

from note import Note, Chord

if sys.platform == "win32":
    mido.set_backend("mido.backends.pygame")  # Was easier to set up on windows
elif sys.platform == "linux":
    mido.set_backend("mido.backends.rtmidi")  # Technically this is default


def _exec_callback(func, *args, **kwargs):
    t = threading.Thread(target=func, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()


class MIDI_Callback:

    callback = namedtuple("Callback", ["chord_name", "func"])

    def __init__(self, verbose=False):
        self.callbacks = []
        self._verbose = verbose
        self._running = False
        self._thread = None

    def add_callback(self, chord_name, func):
        self.callbacks.append(self.callback(chord_name, func))

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
                                    for cb in self.callbacks:
                                        if ident == cb.chord_name:
                                            _exec_callback(cb.func)
                                print(", ".join(identified))
                        else:  # Up
                            down_notes.remove(msg.note)
            print("Loop exit")


def main():
    m = MIDI_Callback()
    m.start()
    input("Press enter to stop\n")
    m.stop()


if __name__ == "__main__":
    main()
