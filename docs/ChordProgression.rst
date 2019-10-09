ChordProgression class
======================
.. py:class:: ChordProgression

    Class used for chord progressions.  Takes a series of Chords.

    .. :py:attribute:: chords

    The tuple of chords represented by this object.

    .. py:method:: check_deque(d: deque)

    Check to see if a deque has the chord in order.

    :param deque d: A deque to compare against
    :return: True or False if it matches.
    :rtype: bool