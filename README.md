# ChordEvents
An easy to use library used to trigger functions when a chord is detected on a MIDI controller

### Installation

```pip install ChordEvents```
Automatically installs pygame and uses that as the backend for mido

### Basic use
```python
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