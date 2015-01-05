# -*- coding: utf-8 -*-

# Copyright (C) 2011  Björn Larsson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#TODO: Write up the documentation for all functions

from exceptions import IndexError, ValueError
from math import floor
import itertools
import re

__all__ = ["levenshtein_distance", "jaccard_distance", "soerensen_index",
           "hamming_distance", "lcs_length", "jaro_distance", "jaro_winkler",
           "dice_coefficient", "tversky_index", "soundex", "nysiis",
           "metaphone", "cologne_phonetic"]


class Matrix(object):
    def __init__(self, rows, cols, default=0):
        if rows < 0 or cols < 0:
            raise ValueError("Array size must not be negative.")

        self.rows = rows
        self.cols = cols
        self.data = [[default for _ in range(cols)] for _ in range(rows)]

    def __setitem__(self, pos, v):
        if 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols:
            self.data[pos[0]][pos[1]] = v
        else:
            raise IndexError("Index out of bounds ( %d, %d )"
            % (pos[0], pos[1]))

    def __getitem__(self, pos):
        if 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols:
            return self.data[pos[0]][pos[1]]
        else:
            raise IndexError("Index out of bounds ( %d, %d )"
            % (pos[0], pos[1]))

    def __str__(self):
        return '\n'.join(['Row %s = %s' % (i, self.data[i])
                          for i in range(self.rows)])

    def __repr__(self):
        return 'Matrix(%d, %d)' % (self.rows, self.cols)

    def size(self):
        return self.rows, self.cols


def levenshtein_distance(lhs, rhs):
    """
    :param lhs: The object to compare
    :param rhs: The object to compare with
    :return: An int >= 0 representing the Levenshtein Distance.
    :raise: ValueError

    Calculates the Levenshtein distance between two strings as described in
    more detail `here <https://secure.wikimedia
    .org/wikipedia/en/wiki/Levenshtein_distance>`__ .
    """

    if not lhs or not rhs:
        raise ValueError("Input cannot be empty")
    if type(lhs) != type(rhs):
        raise ValueError("Input should be of the same type")

    m = Matrix(len(lhs), len(rhs))

    for i in range(len(lhs)):
        m[i, 0] = i
    for i in range(len(rhs)):
        m[0, i] = i

    for j in range(1, len(rhs)):
        for i in range(1, len(lhs)):
            if lhs[i] == rhs[j]:
                m[i, j] = m[i - 1, j - 1]
            else:
                m[i, j] = min(m[i - 1, j] + 1, m[i, j - 1] + 1,
                              m[i - 1, j - 1] + 1)

    return m[len(lhs) - 1, len(rhs) - 1]


def jaccard_distance(lhs, rhs):
    """
    :param lhs: The object to compare
    :param rhs: The object to compare with
    :return: A float in the range [0.0, 1.0]
    :raise: ValueError

    Calculates the Jaccard Distance for the two objects. The full explanation
    can be found `here <https://secure.wikimedia
    .org/wikipedia/en/wiki/Jaccard_index>`__. The equation used is as
    follows.

    .. math::
        J_{\\delta}(lhs,rhs) = { { |lhs \\cup rhs| - |lhs \cap rhs| } \\over
        |lhs \\cup rhs| }


    """
    if not lhs or not rhs:
        raise ValueError("Input cannot be empty")
    if type(lhs) != type(rhs):
        raise ValueError("Input should be of the same type")

    s1 = set(lhs)
    s2 = set(rhs)

    try:
        return  1 - float(len(s1.intersection(s2))) / float(len(s1.union(s2)))
    except ZeroDivisionError:
        return 1


def hamming_distance(lhs, rhs):
    """
    :param lhs: The object to compare
    :param rhs: The object to compare with
    :return: An int >= 0 representing the Hamming Distance between the two
            objects.
    :raise: ValueError

    Calculates the Hamming Distance between two sequences as described in
    more detail `here <https://secure.wikimedia
    .org/wikipedia/en/wiki/Hamming_distance>`__ .
    """
    if not lhs or not rhs:
        raise ValueError("Input cannot be empty")
    if type(lhs) != type(rhs):
        raise ValueError("Input should be of the same type")

    if len(lhs) == len(rhs):
        return sum(ch1 != ch2 for ch1, ch2 in zip(lhs, rhs))
    else:
        raise ValueError("Iterables should be equal length")


def lcs_length(lhs, rhs):
    """
    :param lhs: The object to compare
    :param rhs: The object to compare with
    :return: An int >= 0 indicating the Longest Common Subsequence.
    :raise: ValueError

    Calculates the longest common subsequence as described in more detail
    `here <https://secure.wikimedia.org/wikipedia/en/wiki/Long
    est_common_subsequence_problem>`__.
    """

    if not lhs or not rhs:
        raise ValueError("Input cannot be empty")
    if type(lhs) != type(rhs):
        raise ValueError("Input should be of the same type")

    m = Matrix(len(lhs) + 1, len(rhs) + 1)

    for i, char1 in zip(range(1, len(lhs) + 1), lhs):
        for j, char2 in zip(range(1, len(rhs) + 1), rhs):
            if char1 == char2:
                m[i, j] = m[i - 1, j - 1] + 1
            else:
                m[i, j] = max(m[i, j - 1], m[i - 1, j])

    return m[len(lhs), len(rhs)]


def _get_prefix(lhs, rhs, max_prefix=4):
    """
    :param lhs:
    :param rhs:
    :param max_prefix:
    :return:
    """
    length = min(len(lhs), len(rhs), max_prefix)

    for i in range(0, length):
        if lhs[i] != rhs[i]:
            return i
    return length


def _get_commons(lhs, rhs, dist):
    """
    :param lhs:
    :param rhs:
    :param dist:
    :return:
    """

    commons = [char for index, char in enumerate(lhs) if char in\
            rhs[int(max(0, index - dist)): int(min(index + dist, len(rhs)))]]
    return commons, len(commons)


def jaro_distance(lhs, rhs):
    """
    :param lhs: The object to compare
    :param rhs: The object to compare with
    :return: A float in the range [0.0, 1.0]. 1.0 denotes a perfect match.
    :raise: ValueError

    Implements the Jaro Distance as described `here <https://secure.wikimedia
    .org/wikipedia/en/wiki/Jaro%E2%80%93Winkler_distance>`__ .

    """
    if not lhs or not rhs:
        raise ValueError("Input cannot be empty")
    if type(lhs) != type(rhs):
        raise ValueError("Input should be of the same type")

    max_range = max(floor(float(max(len(lhs), len(rhs))) / float(2.0)) - 1, 0)

    commons1, _len1 = _get_commons(lhs, rhs, max_range)
    commons2, _len2 = _get_commons(rhs, lhs, max_range)

    if _len1 == 0 or _len2 == 0:
        return 0

    num_transpositions = sum(
        ch1 != ch2 for ch1, ch2 in zip(commons1, commons2)) / 2.0
    return (_len1 / float(len(lhs)) + _len2 / float(len(rhs)) +
            (_len1 - num_transpositions) / float(_len1)) / 3.0


def jaro_winkler(lhs, rhs, prefix_scale=0.1):
    """
    :param lhs: The object to compare
    :param rhs: The object to compare with
    :param prefix_scale: The scale factor to use for common prefixes.  The
        value should not be larger than **0.25**, although this is not enforced
        by the function.
    :return: A float >= 0.0. For 0.0 <= *prefix_scale* <= 0.25.  The return
        value will be in the range [0.0, 1.0]
    :raise: ValueError

    Implements the Jaro Winkler Distance as described `here <https://secure
    .wikimedia.org/wikipedia/en/wiki/Jaro%E2%80%93Winkler_distance>`__ .

    The Jaro Winkler favours strings with a common prefix. The weight given
    to strings with a common prefix is controlled using the *prefix_scale*
    parameter. The standard value for *prefix_scale* for the Jaro Winkler
    distance is 0.1 and the value should normally not be greater than 0.5 as
    this could produce distance values greater than 1.0.

    For the common prefix, a maximum of 4 characters will be considered.
    """

    if not lhs or not rhs:
        raise ValueError("Input cannot be empty")
    if type(lhs) != type(rhs):
        raise ValueError("Input should be of the same type")

    dist = jaro_distance(lhs, rhs)
    prefix = _get_prefix(lhs, rhs)
    return dist + (prefix * prefix_scale * (1 - dist))


def dice_coefficient(lhs, rhs):
    """
    :param lhs: The object to compare
    :param rhs: The object to compare with
    :return: A float in the range [0.0, 1.0]
    :raise: ValueError

    Calculates the dice coefficient as described `here <https://secure.wikimedi
    a.org/wikipedia/en/wiki/Dice%27s_coefficient>`__ using the equation.

    .. math::
        s = \\frac{2 * | lhs \cap rhs |}{| lhs | + | rhs |}

    When comparing strings, the bigrams are calculated for the both strings
    and they are then compared, using the above equation.
    """

    if not lhs or not rhs:
        raise ValueError("Input can not be empty")
    if type(lhs) != type(rhs):
        raise ValueError("Input should be of the same type")

    if isinstance(lhs, (str, unicode)) and isinstance(rhs, (str, unicode)):
        #Generate the bigrams
        lhs = [lhs[index:index + 2] for index, _ in enumerate(lhs[0:-1])]
        rhs = [rhs[index:index + 2] for index, _ in enumerate(rhs[0:-1])]

    inter = len(set(lhs).intersection(set(rhs)))
    return (2 * inter) / float(len(lhs) + len(rhs))


def tversky_index(lhs, rhs, alpha, beta):
    """
    :param lhs: The object to compare
    :param rhs: The object to compare with
    :param alpha:
    :param beta:
    :return: A float in the range [0.0, 1.0]
    :raise: ValueError

    Calculates the Tversky index for the two objects,
    as described `here <http://en.wikipedia.org/wiki/Tversky_index>`__

    .. math::
        S(lhs, rhs) = \\frac{| lhs \\cap rhs |}{| lhs \\cap rhs | + \\alpha
        | lhs - rhs | + \\beta | rhs - lhs |}

    When comparing strings, the bigrams for the both strings are calculated
    and they are then compared using the above equation.
    """
    if alpha <= 0 or beta <= 0:
        raise ValueError("Alpha and Beta must be greater than 0")
    if not lhs or not rhs:
        raise ValueError("Input can not be empty")
    if type(lhs) != type(rhs):
        raise ValueError("Input must be of the same type")

    if isinstance(lhs, (str, unicode)) and isinstance(rhs, (str, unicode)):
        lhs = [lhs[index:index + 2] for index, _ in enumerate(lhs[0:-1])]
        rhs = [rhs[index:index + 2] for index, _ in enumerate(rhs[0:-1])]

    lhs = set(lhs)
    rhs = set(rhs)

    return float(len(lhs & rhs)) /\
           (float(len(lhs & rhs)) + alpha * len(lhs - rhs) +
            beta * len(rhs - lhs))


def soundex(name):
    """
    :param name: The name to be encoded
    :type name: str, unicode
    :return: The encoded string
    :raise: ValueError

    Implements the American Soundex Algorithm. The algorithm is described on
    `Wikipedia <https://secure.wikimedia.org/wikipedia/en/wiki/Soundex>`__.

    Calculates a 4 char code for the provided name formatted as LDDD,
    where L is an upper case letter and D is a digit. If the resulting code
    is shorter than 4 char, it is padded with zeros.

    .. note:: This implement ation follows the standard American Soundex
        implementation. There are `other <http://creativyst
        .com/Doc/Articles/SoundEx1/SoundEx1.htm>`__ suggested implementations
        where the letters AEIOUHWY are first encoded as 0 and then removed
        after duplicates have removed. One example where this would make a
        difference is the word "HERMAN" that encodes to H650 using classic
        Soundex and to H655 using the suggested change.
    """

    if not name:
        raise ValueError("String can not be empty")
    if not isinstance(name, (str, unicode)):
        raise ValueError("Input must be string or unicode")

    KEY_LENGTH = 4

    digit = {'B': '1', 'F': '1', 'P': '1', 'V': '1',
             'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2',
             'X': '2', 'Z': '2',
             'D': '3', 'T': '3',
             'L': '4',
             'M': '5', 'N': '5',
             'R': '6'}

    name = str(name).upper()
    name = re.sub(r'[^A-Z]+', '', name)
    name = re.sub(r'(?!^)[AEHIOUWY]', '', name)

    code = name[0]

    digits = [digit[char] for char in name[1:]]

    #Remove all adjacent duplicates
    digits = [k for k, _ in itertools.groupby(digits)]

    code += ''.join(digits) + KEY_LENGTH * "0"

    #Pad with 0 and return the KEY_LENGTH char key
    return code[:KEY_LENGTH]


def nysiis(name, truncate=True):
    """
    :param name: The name to be encoded
    :type name: str, unicode
    :param truncate: Flag to control  if the returned code should be
        truncated to 6 chars or not. For a true NYSIIS implementation,
        this should be True.
    :type truncate: bool
    :return: The encoded string
    :raise: ValueError

    Implements the original New York State Identification and Intelligence
    System ( NYSIIS ) phonetic algorithm. The algorithm is described on `this
    <http://dropby.com/NYSIIS.html>`__ page and on `Wikipedia <http://en
    .wikipedia.org/wiki/New_York_State_
    Identification_and_Intelligence_System>`__ .

    For the standard NYSIIS algorithm, the resulting code is truncated to a
    maximum of 6 characters, this could be changed by passing *truncate* =
    False to return the full length codes.

    .. note:: There appears to be an error in the description in the
        `Wikipedia <http://en.wikipedia
        .org/wiki/New_York_State_Identification_and_Intelligence_System>`__
        description of the algorithm. It is stated that KN -> N in the
        beginning of the word, however several other sources suggest that it
        should be KN -> NN so that KNUTH -> NNAT. This is the functionality
        that has been implemented.
    """

    if not name:
        raise ValueError("Name can not be empty")
    if not isinstance(name, (str, unicode)):
        raise ValueError("Name must be sting or unicode")

    vowels = ["A", "E", "I", "U", "O"]

    name = name.upper().strip()

    pre = [
        (r'\s+JR\.?\s{0,}', ''),
        (r'\s+SR\.?\s{0,}', ''),
        (r'\s+[IVXMC]+\.?\s{0,}', ''),
        (r'[^A-Z]+', ''),
        (r'^MAC', 'MCC'),
        (r'^KN', 'NN'),
        (r'K', 'C'),
        (r'^P[HF]', 'FF'),
        (r'^SCH', 'SSS'),
        (r'[EI]E$', 'Y'),
        (r'[DRN]T$', 'D'),
        (r'[RN]D$', 'D')
    ]

    post = [
        (r'EV', 'AF'),
        (r'[AEIOU]', 'A'),
        (r'Q', 'G'),
        (r'Z', 'S'),
        (r'M', 'N'),
        (r'KN', 'N'),
        (r'K', 'C'),
        (r'SCH', 'SSS'),
        (r'PH', 'FF'),
        (r'([^%s])H' % ''.join(vowels), r'\1'),
        (r'(.)H[^%s]' % ''.join(vowels), r'\1'),
        (r'[%s]W' % ''.join(vowels), 'A'),
        (r'S$', ''),
        (r'AY$', 'Y'),
        (r'A+$', '')
    ]

    for reg, sub in pre:
        name = re.sub(reg, sub, name)

    try:
        code = name[0]
    except IndexError:
        raise ValueError("String is not encodable")

    name = name[1:]

    for reg, sub in post:
        name = re.sub(reg, sub, name)

    #remove all adjacent duplicates
    code += ''.join([key for key, _ in itertools.groupby(name)])

    if len(code) > 6 and truncate:
        return code[:6]
    else:
        return code


def metaphone(name, length=4):
    """
    :param name: The name to be encoded
    :type name: str, unicode
    :param length: The maximum length to use for the resulting code
    :type length: int
    :return: A string of maximum length *length*
    :raise: ValueError

    There appear to be several different ways to implement the Metaphone
    algorithm. This seems to come from the fact that the description and the
    implementation of the original algorithm from Lawrence Philips do not
    correspond entirely.

    This implementation aims at following the inte rpreted implementation
    presented by `Michael Kuhn <http://aspell.net/metaphone/metaphone-kuhn
    .txt>`__.

    Normally the first four characters of the code are used for the Metaphone,
    but the maximum length of the returned code can be controlled by passing
    the *length* argument.
    """

    if not isinstance(length, int):
        raise ValueError("Length must be an integer")
    if length <= 0:
        raise ValueError("Length must be 0 or greater")
    if not name:
        raise ValueError("Name can not be empty")
    if not isinstance(name, (str, unicode)):
        raise ValueError("Name must be string or unicode")

    vowels = ["A", "E", "I", "O", "U"]

    rules = [
        (r'[^A-Z]+', ''),
        (r'([ABCDEFHIJKLMNOPQRSTUVXYZ])\1+', r'\1'),
        (r'^AE', 'E'),
        (r'^[GKP]N', 'N'),
        (r'^WR', 'R'),
        (r'^X', 'S'),
        (r'^WH', 'W'),
        (r'MB$', 'M'),
        (r'X', 'KS'),
        (r'(?!^)C(IA|H)', 'X'),
        (r'(?!^)C(?=[IEY])', 'S'),
        (r'(?<=\SS)C(?=[IEY])', 'S'),
        (r'C', 'K'),
        (r'(?!^)D(?=G([IEY]\S+))', 'J'),
        (r'D', 'T'),
        (r'(?!^)G(?=H[^%s])' % ''.join(vowels), ''),
        (r'(?!^)GN(?:ED)?$', ''),
        (r'(?<=\SD)G(?=[IEY]\S+)', ''),
        (r'^G(?=[IEY])', 'J'),
        (r'(?<!G)G(?=[IEY])', 'J'),
        (r'G', 'K'),
        (r'(?<=[%s])H(?=\b|[^%s])' % (''.join(vowels), ''.join(vowels)), ''),
        (r'(?<=\S[CSPTG]H)H(?=\S+)', ''),
        (r'(?<=C)K', ''),
        (r'P(?=H)', 'F'),
        (r'Q', 'K'),
        (r'SH', 'X'),
        (r'(?!^)S(?=I[OA]\S+)', 'X'),
        (r'(?!^)T(?=I[OA]\S+)', 'X'),
        (r'TH', '0'),
        (r'(?!^)T(?=CH\S+)', ''),
        (r'V', 'F'),
        (r'W(?=[^%s])' % ''.join(vowels), ''),
        (r'Y(?=\b|[^%s])' % ''.join(vowels), ''),
        (r'Z', 'S'),
        (r'(?!^)[%s]+' % ''.join(vowels), ''),
    ]

    name = name.upper().strip()

    for rule in rules:
        name = re.sub(rule[0], rule[1], name)

    if len(name) > length:
        return name[:length]
    else:
        return name


def cologne_phonetic(name):
    """
    :param name: The name to be encoded
    :type name: str, unicode
    :returns: The encoded string
    :raise: ValueError

    The Cologne Phonetic Algorithm is a phonetic encoding algorithm
    specialised for the german language. A description in english can be
    found on the manual page for `this <http://commons.apache
    .org/codec/apidocs/org/apache/commons/codec/language/ColognePhonetic
    .html>`__ Java implementation.


    Wikipedia has a `description <https://secure.wikimedia
    .org/wikipedia/de/wiki/K%C3%B6lner_Phonetik>`__ of the algorithm in german.


    Unlike most other phonetic encoding algorithms, the Cologne Phonetic is
    not truncated to a specific length but rather returned in its full length.

    .. note:: As suggested in the Wikipedia description,
        umlauts and ß are encoded as 0
    """

    if not name:
        raise ValueError("Name can not be empty")
    if not isinstance(name, (str, unicode)):
        raise ValueError("Name must be string or unicode")

    name = name.upper().strip()

    rules = [
        (r'[^A-Z]+', ''),
        (r'P(?!H)', '1'),
        (r'[DT](?![CSZ])', '2'),
        (r'P(?=H)', '3'),
        (r'(?<=^)C(?=[AHKLOQRUX])', '4'),
        (r'(?<![SZ])C(?=[AHKOQUX])', '4'),
        (r'(<![CKQ])X', '48'),
        (r'(?<=[SZ])C', '8'),
        (r'(?<=^)C(?![AHKLOQRUX])', '8'),
        (r'C(?![AHKOQUX])', '8'),
        (r'[DT](?=[CSZ])', ''),
        (r'(?<=[CKQ])X', ''),
        (r'[FVW]', '3'),
        (r'H', ''),
        (r'B', '1'),
        (r'[GKQ]', '4'),
        (r'[SZ]', '8'),
        (r'R', '7'),
        (r'L', '5'),
        (r'[MN]', '6'),
        (r'[AEIJOUYÄÖÜß]+', '0'),
        #remove duplicates
        (r'(\d)\1+', r'\1'),
        #Remove all 0
        (r'0+', ''),
        ]

    for rule in rules:
        name = re.sub(rule[0], rule[1], name)

    return name
