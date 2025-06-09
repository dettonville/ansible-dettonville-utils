# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r'''
  name: to_markdown
  short_description: Converts a list of flat dictionaries to markdown format
  version_added: 2024.6.5
  author: Lee Johnson
  description:
    - Converts a list of flat dictionaries to markdown format.
  options:
    _input:
      description: The list of dictionaries that should be converted to the markdown format.
      type: list
      required: true
'''

EXAMPLES = r'''
- name: Define a list of dictionaries
  ansible.builtin.set_fact:
    export_list: 
      - { key1: "value11", key2: "value12", key3: "value13", key4: "value14" }
      - { key1: "value21", key2: "value22", key3: "value23", key4: "value24" }
      - { key1: "value31", key2: "value32", key3: "value33", key4: "value34" }
      - { key1: "value41", key2: "value42", key3: "value43", key4: "value44" }

- name: Write dictionary to markdown
  ansible.builtin.copy:
    dest: /tmp/test.md
    content: '{{ export_list | dettonville.utils.to_markdown }}'

# Produces the markdown:
# | key1 | key2 | key3 | key4 |
# | --- | --- | --- | --- |
# | value11 | value12 | value13 | value14 |
# | value21 | value22 | value23 | value24 |
# | value31 | value32 | value33 | value34 |
# | value41 | value42 | value43 | value44 |
'''

RETURN = r'''
  _value:
    description: A string formatted as markdown.
    type: string
'''


__metaclass__ = type

import sys
import logging
import pprint

from ansible.errors import AnsibleFilterError
from ansible.module_utils.six.moves import StringIO
from ansible.module_utils.six.moves.configparser import ConfigParser
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.dettonville.utils.plugins.module_utils.export_dict_utils import write_markdown_string


def to_markdown(export_list: list, column_list=[]):
    ''' Read the given dict and return an markdown formatted string '''

    if not isinstance(export_list, list):
        raise AnsibleFilterError(f'to_markdown requires a list, got {type(export_list)}')

    logging.info("export_list => %s" % pprint.pformat(export_list))

    if len(column_list) == 0 and len(export_list) > 0:
        column_list = []
        # Derive column_list for the csv file based on first row of export_list.

        if sys.version_info >= (3, 7):
            column_keys = list(export_list[0].keys())
        else:
            # the insertion-order preservation nature of dict objects has been declared to be an official part
            #  of the Python language spec for versions 3.7+
            # ref: https://stackoverflow.com/questions/5629023/order-of-keys-in-dictionaries-in-old-versions-of-python
            column_keys = sorted(list(export_list[0].keys()))

        for column_name in column_keys:
            column_list.append({
                "name": column_name,
                "header": column_name
            })

    logging.debug("column_list => %s" % pprint.pformat(column_list))

    for column in column_list:
        column_name = column['name']
        if not column_name:
            raise AnsibleFilterError("Column name not found: %s" % column)

    return write_markdown_string(export_list=export_list, column_list=column_list)


class FilterModule(object):
    ''' Query filter '''

    def filters(self):

        return {
            'to_markdown': to_markdown
        }
