Note class
==========
.. py:class:: Note(*args, note_str=None, note=None, octave=None, midi=None)

    Can be created using keywords or implicitly.  1 string argument is mapped to ``note_str``, 1 str and 1 int arguments are mapped to ``note`` and ``octave``, 1 int argument is mapped to ``midi``.

    :param \*args: When no keywords are specified, attempts to implicitly map to another parameter or parameters.
    :param str note_str: The ASCII representation of a note ordered as [note letter][optional accidental][octave number], for example A4, C#2.  Also accepts lower case, and normally unusual accidentals, for example fb4 would create a note E4.
    :param str note: The note letter, or more formally the alphabetical representation of the pitch class.  Accidentals are allowed.  Can't be used with ``note_str``, but requires that ``octave`` be specified.
    :param int octave: The octave of the note.  Can't be used with ``note_str``, but requires that ``note`` be specified.
    :raises TypeError: When ``note_str`` is called with either ``note`` or ``octave``.
    :raises TypeError: When implicit variable mapping fails, or when not enough or too many variables are given.


    .. py:attribute:: note

    The note letter, e.g. 'A' or 'F#'.


    .. py:attribute:: pc

    Pitch class, see https://en.wikipedia.org/wiki/Pitch_class#Integer_notation.


    .. py:attribute:: octave

    Octave number for the note.


    .. py:attribute:: midi

    MIDI note number.


    .. py:attribute:: freq

    Frequency of the note in Hz.


    .. py:attribute:: pitch_class_map

    ``dict`` Class attribute that maps pitch classes (:py:attr:`pc`) to :py:attr:`note`.


    .. py:attribute:: pitch_class_map_complement

    ``dict`` Class attribute, the inverse of ``pitch_class_map``.


    .. py:classmethod:: _note_octave_to_midi(note, octave)

    Used to get the ``midi`` value for a given ``note`` and ``octave``.


    .. py:classmethod:: _midi_to_note_octave(m)

    Takes a MIDI number ``m`` and returns a ``note`` and ``octave``.