Sequence class
==============
.. py:class:: Sequence

    Child class of :py:class:`NoteList`, uses same constructor.  Is hashable.  Contains :py:class:`Note` objects, as well as functions to analyze chords.  Accepts either a single iterable :py:class:`Note`\ s, or a bunch of :py:class:`Note`\ s.  Typically constructed using the inherited functions :py:meth:`NoteList.from_ascii` or :py:meth:`NoteList.from_midi_list`.  While similar to :py:class:`NoteList`, :py:class:`Sequence` can be used with :py:class:`MIDIEventLoop`.

    :raises ValueError: When more than :py:attr:`maxlen` objects are passed for construction.


    .. py:attribute:: maxlen

    Default is 16.  Maximum length to use when comparing to a ``deque``.  Also what is used for the :py:attr:`MIDIEventLoop.recent_notes` ``deque`` max length.

