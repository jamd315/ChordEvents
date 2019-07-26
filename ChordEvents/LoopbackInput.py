import queue

import mido

class LoopbackInput(mido.ports.BaseInput):
    """Used for testing"""
    def __init__(self, *args, **kwargs):
        try:
            if kwargs["verbose"]:
                self.verbose = True
        except KeyError:
            self.verbose = False
        super().__init__()
    
    def _open(self, **kwargs):
        self._my_queue = queue.Queue()
        if self.verbose:
            print("Opened loopback port")
    
    def _close(self, **kwargs):
        self._my_queue = queue.Queue()  # Clear it with a new queue
        if self.verbose:
            print("Closed loopback port")

    def _receive(self, block=True):
        if block:
            return self._my_queue.get()
        else:
            try:
                return self._my_queue.get(block=False)
            except queue.Empty:
                return
    
    def create_msg(self, msg):
        """Sends a MIDI message to the port to be echoed to the """
        self._my_queue.put(msg)
