LoopbackPort class
==================
.. py:class:: LoopbackPort

    """Used for testing.  Similar to undocumented mido.ports.EchoPort, but copies some code from the rtmidi backend to emulate callbacks.  Accepts any arguments the ``mido.ports.BaseIOPort`` would.  ``send`` and ``receive`` work similar to how they do for the rtmidi backend, with less error checking and overall complexity."""