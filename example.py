import mido
import MIDIEvents

MEL = MIDIEvents.MIDIEventLoop()


# Most chords in this list are valid
# https://en.wikipedia.org/wiki/List_of_chords
@MEL.on_notes("C4 Major")
def do_work():
    print("Did a thing")


input("This is a blocking function so that the script doesn't end.\n")
