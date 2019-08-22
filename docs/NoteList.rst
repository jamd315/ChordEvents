NoteList class
==============
.. py:class:: NoteList(*args)

    Base class that other note lists (e.g. :py:class:`Chord` or :py:class:`Sequence`) inherit from.

    :param \*args: An iterable or nested iterable up to :py:attr:`max_depth` of either :py:class:`Note` objects or ``int``\ s representing MIDI numbers.  Can also take a :py:class:`NoteList` as a constructor, mainly intended for use by child classes.
    :raises ValueError: If the :py:attr:`max_depth` is exceeded but no valid objects are found.
    :raises TypeError: If a non-iterable is passed to the constructor.


    .. py:attribute:: max_depth

    Default is 5.  Class attribute for how deep the constructor searches for valid variables.


    .. py:attribute:: notes

    This attribute is a property.  Returns a sorted ``tuple`` of :py:class:`Note` objects.  When setting this attribute, it expects an iterable of :py:class:`Note` objects, that it will then sort and store as a tuple.


    .. py:classmethod:: from_ascii(note_string)

    :param str note_string: Space or comma-space separated ASCII notes
    :return: :py:class:`NoteList` or child class with the :py:class:`Note`\ s.
    :rtype: NoteList or child class


    .. py:classmethod:: from_midi_list(midi_list)

    :param list midi_list: List of integers representing MIDI note codes.
    :return: :py:class:`NoteList` or child class with the :py:class:`Note`\ s.
    :rtype: NoteList or child class