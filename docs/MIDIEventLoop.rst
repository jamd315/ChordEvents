MIDIEventLoop class
===================
.. py:class:: MIDIEventLoop(port)

    The event loop that watches for :py:class:`Chord`\ s or :py:class:`Sequence`\ s and other children of :py:class:`NoteList` and calls the event handlers.  Uses callbacks if the backend supports it.  Otherwise an internal loop will need to be started with :py:meth:`start` and :py:meth:`stop`\ .

    :param port: ``mido`` port.  Default is "default", which gets the 1st port from ``mido.get_input_names()``.  Also accepts strings as returned form ``mido.get_input_names()``.
    :type port: str or ``mido`` port
    :raises RunTimeError: When using the default port and but ``mido.get_input_names()`` doesn't return any ports.
    :raises TypeError: When something besides a ``mido`` port or ``str`` is passed to the ``port`` parameter.


    .. py:attribute:: down_notes

    ``set`` of notes that are currently down.  Used to determine when a :py:class:`Chord` is being pressed.


    .. py:attribute:: recent_notes

    ``deque`` of the last n notes, n is the :py:meth:`Sequence.maxlen` class attribute.


    .. py:attribute:: chord_handlers

    ``dict`` of :py:class:`Chord`\ s mapped to a list of of handler functions.

    .. py:attribute:: sequence_handlers

    ``dict`` of :py:class:`Sequence`\ s mapped to a list of handler functions.


    .. py:attribute:: port

    ``mido`` port being used


    .. py:attribute:: running_handler_threads

    A ``list`` of the current running handlers threads.


    .. py:method:: on_notes(notes_obj)

    Decorator function similar to :py:meth:`add_handler`\.  Function is spawned in a new thread.

    :param notes_obj: :py:class:`NoteList` or child class.  If a string is passed, will try to resolve to a :py:class:`Chord` similar to the output of :py:meth:`Chord.identify`


    .. py:method:: add_handler(func, notes_obj)

    Create a new event handler that runs the function when a ``notes_obj`` is pressed

    :param function func:  Function to call when the chord is detected.  Will be spawned in a new daemon thread.
    :param notes_obj: :py:class:`NoteList` or child class.  If a string is passed, will try to resolve to a :py:class:`Chord` similar to the output of :py:meth:`Chord.identify`


    .. py:method:: clear_handlers(notes_obj=None)

    Clear :py:attr:`chord_handlers` and/or :py:attr:`sequence_handlers` for a given ``notes_obj``.  Default is to clear all handlers if ``notes_obj`` is not specified.

    :param notes_obj: Default ``None``\.  :py:class:`NoteList` or child class.  If a string is passed, will try to resolve to a :py:class:`Chord` similar to the output of :py:meth:`Chord.identify`


    .. py:method:: start(blocking=False)

    Only required when backend doesn't support callbacks.  Start the main loop, used to process MIDI and trigger event handlers.  Loop can be stopped with :py:meth:`stop`.
    Warns when called while using a backend that supports callbacks.

    :param bool blocking: Default false.  If true, will block until a handler calls :py:meth:`stop` on the :py:class:`MIDIEventLoop` object.


    .. py:method:: stop

    Only required when backend doesn't support callbacks.  Stop the main loop.  Loop can be restarted with :py:meth:`start` after being stopped.
    Warns when called while using a backend that supports callbacks.


    .. py:staticmethod:: _resolve_notes_obj(notes_obj)

    Typically called when another function needs to make sure a ``notes_obj`` is legal, e.g. when using it as a parameter.

    :param notes_obj: Default ``None``\.  :py:class:`NoteList` or child class.  If a string is passed, will try to resolve to a :py:class:`Chord` similar to the output of :py:meth:`Chord.identify`
    :return: notes_obj
    :rtype: Chord or Sequence
    :raises AssertionError: When something besides a :py:class:`Chord` or :py:class:`Sequence` or ``str`` is passed to it.