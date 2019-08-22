Chord class
===========
.. py:class:: Chord

    Child class of :py:class:`NoteList`, uses same constructor.  Is hashable.  Contains :py:class:`Note` objects, as well as functions to analyze chords.  Accepts either a single iterable :py:class:`Note`\ s, or a bunch of :py:class:`Note`\ s.  Typically constructed using the inherited functions :py:meth:`NoteList.from_ascii` or :py:meth:`NoteList.from_midi_list`


    .. py:attribute:: chords

    Class attribute, dictionary of chord names and semitones from chords.json, exported from https://en.wikipedia.org/wiki/List_of_chords


    .. py:method:: identify

    Identify what chord this is.  Most chords here are valid.  https://en.wikipedia.org/wiki/List_of_chords.  Returns a list of chord names that match the current :py:class:`Chord` object.

    :return: List of chord names in format "note_ascii chord_name", e.g. "C4 Major"


    .. py:classmethod:: from_ident(ident_chord_name)

    Used to create a :py:class:`Chord` from an identified chord, e.g. 'C4 Major.

    :param str ident_chord_name: Chord name similar to what :py:meth:`identify` outputs.
    :raises AssertionEror: If ``ident_chord_name`` doesn't have a space in it to separate the chord name from the base.


    .. py:classmethod:: from_note_chord(note_obj, chord_name)

    Used to create a :py:class:`Chord` from a :py:class:`Note` and a chord name

    :param Note note_obj: :py:class:`Note` object representing the base note of the chord
    :param str chord_name: String name of chord, see names of chord in chords.json.  e.g. "Major", or "Harmonic seventh"
    :return: :py:class:`Chord`


    .. py:classmethod:: _get_semitones_from_chord_name(chord_name)

    Return the 1st semitone from the list of semitones in chords.json for a given ``chord_name``

    :param str chord_name: String name of chord, see names of chord in chords.json.  e.g. "Major", or "Harmonic seventh"
    :return: Semitones from the base for each note in a chord
    :rtype: list of ints
    :raises ValueError: When the function can't find a chord with the ``chord_name``