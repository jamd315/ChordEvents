import time

import ChordEvents


CEL = ChordEvents.ChordEventLoop()

@CEL.on_chord("D2 Major")
def my_event_handler():
    print("doing a thing...")
    time.sleep(5)
    print("did a thing")

@CEL.on_chord("C4 Major")
def stop_CEL():
    CEL.stop()

CEL.start(blocking=True)
