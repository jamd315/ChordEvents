# ChordEvents
An easy to use library used to trigger functions when a chord is detected on a MIDI controller.  Currently still in development.


## Installation

#### Requirements

Uses ``colorama`` to make pretty logs, should install automatically.  Uses python-rtmidi for the backend by default.  See [the python-rtmidi installation requirements](https://spotlightkid.github.io/python-rtmidi/installation.html#requirements)

After reqirements have been satisfied
```pip install ChordEvents```

##### Installing on Debian based Linux
```
sudo apt install build-essential python-dev python3-dev libasound2-dev libjack-jackd2-dev
pip3 install python-rtmidi
```

##### Installing on Windows
Windows is trickier, see [the python-rtmidi Windows install instructions](https://spotlightkid.github.io/python-rtmidi/install-windows.html).  Sometimes ```pip install python-rtmidi``` is all you need.


### Basic use
-------------

```python
import time

import ChordEvents

CEL = ChordEvents.ChordEventLoop()


# Most chords in this list are valid
# https://en.wikipedia.org/wiki/List_of_chords
@CEL.on_chord("C4 Major")
def do_work():
    print("Doing work...")
    time.sleep(5)
    print("Did work")


# There's also a blocking version, CEL.start(blocking=True)
# Make sure to have an event handler or separate thread that can call CEL.stop()
CEL.start()
input("Press enter to stop\n")
CEL.stop()

```