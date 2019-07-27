import logging
import queue

import mido

logger = logging.getLogger(__name__)


class LoopbackInput(mido.ports.BaseInput):
    """Used for testing"""
    def _open(self, **kwargs):
        self._my_queue = queue.Queue()
        logger.info("Opened loopback port")
    
    def _close(self, **kwargs):
        self._my_queue = queue.Queue()  # Clear it with a new queue
        logger.info("Closed loopback port")

    def _receive(self, block=True):
        if block:
            return self._my_queue.get()
        else:
            try:
                return self._my_queue.get(block=False)
            except queue.Empty:
                return
    
    def create_msg(self, msg):
        """Sends a MIDI message to the port to be echoed to any ports using this as an input"""
        logger.debug("Created message for LoopbackInput")
        self._my_queue.put(msg)
