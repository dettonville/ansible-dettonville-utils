# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import os
import re

import yaml
#import copy
import pprint
import logging

from collections import OrderedDict

from operator import itemgetter as i
from functools import cmp_to_key

from ansible.errors import AnsibleLookupError
from ansible.module_utils.compat.importlib import import_module


FQCN_RE = re.compile(r'^[A-Za-z0-9_]+\.[A-Za-z0-9_]+$')


def load_collection_meta_manifest(manifest_path):
    with open(manifest_path, 'rb') as f:
        meta = json.load(f)
    return {
        'version': meta['collection_info']['version'],
    }


def load_collection_meta_galaxy(galaxy_path, no_version='*'):
    with open(galaxy_path, 'rb') as f:
        meta = yaml.safe_load(f)
    return {
        'version': meta.get('version') or no_version,
    }


def load_collection_meta(collection_pkg, no_version='*'):
    path = os.path.dirname(collection_pkg.__file__)

    # Try to load MANIFEST.json
    manifest_path = os.path.join(path, 'MANIFEST.json')
    if os.path.exists(manifest_path):
        return load_collection_meta_manifest(manifest_path)

    # Try to load galaxy.y(a)ml
    galaxy_path = os.path.join(path, 'galaxy.yml')
    galaxy_alt_path = os.path.join(path, 'galaxy.yaml')
    # galaxy.yaml was only supported in ansible-base 2.10 and ansible-core 2.11. Support was removed
    # in https://github.com/ansible/ansible/commit/595413d11346b6f26bb3d9df2d8e05f2747508a3 for
    # ansible-core 2.12.
    for path in (galaxy_path, galaxy_alt_path):
        if os.path.exists(path):
            return load_collection_meta_galaxy(path, no_version=no_version)

    return {}


def get_collection_version(terms, not_found=None, no_version='*'):
    result = []
    for term in terms:
        if not FQCN_RE.match(term):
            raise AnsibleLookupError('"{term}" is not a FQCN'.format(term=term))

        try:
            collection_pkg = import_module('ansible_collections.{fqcn}'.format(fqcn=term))
        except ImportError:
            # Collection not found
            result.append(not_found)
            continue

        try:
            data = load_collection_meta(collection_pkg, no_version=no_version)
        except Exception as exc:
            raise AnsibleLookupError('Error while loading metadata for {fqcn}: {error}'.format(fqcn=term, error=exc))

        result.append(data.get('version', no_version))

    return result


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

# ref: https://stackoverflow.com/questions/9001509/how-do-i-sort-a-dictionary-by-key
# ref: https://stackoverflow.com/questions/72899/how-to-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary-in-python

def sort_dict_keys(my_dict, reverse=False):
    return dict(sorted(my_dict.items(), reverse=reverse))


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


# ref: https://dave.dkjones.org/posts/2013/pretty-print-log-python/
# ref: https://realpython.com/python-pretty-print/
class PrettyLog:
    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        # ref: https://stackoverflow.com/questions/21420243/pretty-printing-ordereddicts-using-pprint
        # ref: https://stackoverflow.com/questions/4301069/any-way-to-properly-pretty-print-ordereddict
        if isinstance(object, OrderedDict):
            return pprint.pformat(dict(self.obj))
        return pprint.pformat(self.obj)
