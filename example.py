import mido
import ChordEvents

CEL = ChordEvents.ChordEventLoop()


# Most chords in this list are valid
# https://en.wikipedia.org/wiki/List_of_chords
@CEL.on_chord("C4 Major")
def do_work():
    print("Did a thing")

input("This is a blocking function so that the script doesn't end.\n")
