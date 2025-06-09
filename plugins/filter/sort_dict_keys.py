# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: sort_dict_keys
  short_description: Sort dictionary keys
  version_added: 3.1.0
  author: Lee Johnson (@lj020326)
  description:
    - Sort dictionary keys.
  positional: reverse
  options:
    _input:
      description: A list of dictionaries
      type: list
      elements: dictionary
      required: true
    reverse:
      description: Set reverse=True to sort keys in descending order.
      type: list
      default: false
      required: false
"""

EXAMPLES = '''
- name: Sort dictionary keys
  ansible.builtin.debug:
    msg: "{{ my_dict | dettonville.utils.sort_dict_keys }}"
  vars:
    my_dict:
      hosts.yml:
        all:
          children:
            app_abc123_qa:
              hosts:
                test123.qa.site1.example.int: {}
            app_abc123_prod:
              hosts:
                test123.prod.site1.example.int: {}
      group_vars/xenv_groups.yml:
        all:
          children:
            app_abc123:
              children:
                app_abc123_qa: {}
                app_abc123_sandbox: {}
                app_abc123_dev: {}
                app_abc123_prod: {}
            ansible_localhost:
              children:
                ansible_localhost_iam: {}
                ansible_controller_iam: {}
  # Produces the sorted dict:
  #
  #  my_dict:
  #    group_vars/xenv_groups.yml:
  #      all:
  #        children:
  #          ansible_localhost:
  #            children:
  #              ansible_controller_iam: {}
  #              ansible_localhost_iam: {}
  #          app_abc123:
  #            children:
  #              app_abc123_dev: {}
  #              app_abc123_prod: {}
  #              app_abc123_qa: {}
  #              app_abc123_sandbox: {}
  #    hosts.yml:
  #      all:
  #        children:
  #          app_abc123_prod:
  #            hosts:
  #              test123.prod.site1.example.int: {}
  #          app_abc123_qa:
  #            hosts:
  #              test123.qa.site1.example.int: {}
'''

RETURN = '''
  _value:
    description: A sorted list containing the dictionaries from the original list.
    type: list
'''

# from ansible.errors import AnsibleFilterError
# from ansible.module_utils.common._collections_compat import Mapping, Sequence
# from ansible.module_utils.six import string_types, text_type

# from operator import itemgetter as i
# from functools import cmp_to_key

# noinspection PyUnresolvedReferences
from ansible_collections.dettonville.utils.plugins.module_utils.utils import sort_dict_keys


class FilterModule(object):

    def filters(self):
        return {
            'sort_dict_keys': self.sort_dictionary_keys
        }

    def sort_dictionary_keys(self, my_dict, reverse=False):
        return sort_dict_keys(my_dict, reverse)
