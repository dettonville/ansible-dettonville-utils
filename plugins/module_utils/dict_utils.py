# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
import copy
import logging

from operator import itemgetter as i
from functools import cmp_to_key


# ref: https://stackoverflow.com/questions/20692710/python-recursively-deleting-dict-keys#20692955
# ref: https://stackoverflow.com/questions/13183501/staticmethod-and-recursion#13183523
def remove_keys_from_object(
        object: any,
        key_patterns: list,
        log_level: str = "INFO"
) -> any:

    logging.basicConfig(
        level=log_level
    )

    logging.debug("key_patterns=%s" % key_patterns)

    # ref: https://stackoverflow.com/questions/3040716/python-elegant-way-to-check-if-at-least-one-regex-in-list-matches-a-string

    # regex_pattern_list = map(re.compile, key_patterns)
    # print("regex_pattern_list=%s" % regex_pattern_list)

    if isinstance(object, dict):
        # the call to `list` is useless for py2 but makes
        # the code py2/py3 compatible
        for key in list(object.keys()):
            # print("key=%s" % key)
            # if any(regex.match(key) for regex in regex_pattern_list):
            # if any(re.match(regex, key) for regex in key_patterns):
            if any(re.search(regex, key) for regex in key_patterns):
                logging.debug("*** regex=%s" % key)
                logging.debug("*** remove key=%s" % key)
                del object[key]
            else:
                remove_keys_from_object(object[key], key_patterns, log_level)
    elif isinstance(object, list):
        for i in reversed(range(len(object))):
            if isinstance(object[i], dict):
                remove_keys_from_object(object[i], key_patterns, log_level)
    else:
        # neither a dict nor a list, do nothing
        pass
    return

def sort_single_key(dict_list: list, sort_key: str) -> list:
    return sorted(dict_list, key=lambda item: item.get(sort_key))

# ref: https://stackoverflow.com/questions/1143671/how-to-sort-objects-by-multiple-keys#1144405
def sort_multi_key(dict_list: list, sort_keys: list) -> list:
    comparers = [
        ((i(col[1:].strip()), -1) if col.startswith('-') else (i(col.strip()), 1))
        for col in sort_keys
    ]

    def cmp(x, y):
        """
        Replacement for built-in function cmp that was removed in Python 3

        Compare the two objects x and y and return an integer according to
        the outcome. The return value is negative if x < y, zero if x == y
        and strictly positive if x > y.

        https://portingguide.readthedocs.io/en/latest/comparisons.html#the-cmp-function
        """

        return (x > y) - (x < y)

    def comparer(left, right):
        comparer_iter = (
            cmp(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)

    return sorted(dict_list, key=cmp_to_key(comparer))
