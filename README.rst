##########
MIDIEvents
##########
.. image:: https://dev.azure.com/lizardswimmer/MIDIEvents/_apis/build/status/jamd315.MIDIEvents?branchName=master
   :target: https://dev.azure.com/lizardswimmer/MIDIEvents/_build/latest?definitionId=1&branchName=master
   :alt: Build Status

.. image:: https://readthedocs.org/projects/midievents/badge/
   :target: https://midievents.readthedocs.io/en/latest/
   :alt: Documentation

An easy to use library used to trigger functions when a chord is detected on a MIDI controller.  Currently still in development.

Documentation on Read The Docs at https://midievents.readthedocs.io/en/latest/

Installation
============
After requirements have been satisfied, ``pip install MIDIEvents``

Requirements
~~~~~~~~~~~~

Python requirements are installed automatically during installing.  python-rtmidi does require some additional C libraries that aren't installed during installation.

* Uses `mido <https://mido.readthedocs.io/en/latest/>`_ for MIDI interface and low level notes.  Any MIDO backend is supported, but only those python-rtmidi and pygame are tested.
* Uses `python-rtmidi <http://trac.chrisarndt.de/code/wiki/python-rtmidi>`_ for the backend by default.  See `the python-rtmidi installation requirements <https://spotlightkid.github.io/python-rtmidi/installation.html#requirements>`_.
* Can also use `pygame <https://www.pygame.org>`_ as the backend, but won't support callbacks.
* Uses `colorama <https://github.com/tartley/colorama>`_ to make pretty logs.


Installing on Debian based Linux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt install build-essential python-dev python3-dev libasound2-dev libjack-jackd2-dev
   pip3 install python-rtmidi


Installing on Windows
~~~~~~~~~~~~~~~~~~~~~

Windows is trickier, see `the python-rtmidi Windows install instructions <https://spotlightkid.github.io/python-rtmidi/install-windows.html>`_.  Sometimes ``pip install python-rtmidi`` is all you need.

Basic use
=========


.. code-block:: python

    import MIDIEvents

    MEL = MIDIEvents.MIDIEventLoop()


    # Most chords in this list are valid
    # https://en.wikipedia.org/wiki/List_of_chords
    @MEL.on_notes("C4 Major")
    def do_work():
        print("Did a thing")


    input("This is a blocking function so that the script doesn't end.\n")
