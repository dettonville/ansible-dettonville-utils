# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: sort_dict_list
  short_description: Sort list of dictionaries by specified key(s)
  version_added: 3.1.0
  author: Lee Johnson (@lj020326)
  description:
    - Sort list of dictionaries by a specified key(s).
  positional: sort_keys
  options:
    _input:
      description: A list of dictionaries
      type: list
      elements: dictionary
      required: true
    sort_keys:
      description: The attributes to use as the sort keys.
      type: list
      required: true
"""

EXAMPLES = '''
- name: Sort a list of dictionaries based on single key sort
  ansible.builtin.debug:
    msg: "{{ my_list | dettonville.utils.sort_dict_list('name') }}"
  vars:
    my_list:
      - name: value
        foo: bar
      - name: other_value
        baz: bar
  # Produces the sorted list:
  #
  #  my_list:
  #    - name: other_value
  #      baz: bar
  #    - name: value
  #      foo: bar

- name: Sort a list of dictionaries based on multiple key sort
  ansible.builtin.debug:
    msg: "{{ my_list | dettonville.utils.sort_dict_list(['platform_id','address','username']) }}"
  vars:
    my_list:
    - address: 172.31.25.54
      automatic_management_enabled: true
      domain_type: local
      platform_account_type: recon
      platform_id: WND-Local-Managed-DMZ
      platform_logon_domain: 172.31.25.54
      platform_notes: WINANSD1S4.dettonville.int
      safe: A-T-careconlocal
      username: careconlocal
    - address: 172.31.25.54
      automatic_management_enabled: true
      domain_type: local
      groups:
      - Administrators
      local_admin_username: administrator
      managed: true
      platform_account_type: platform
      platform_id: WND-Local-Managed-DMZ
      platform_logon_domain: 172.31.25.54
      platform_notes: WINANSD1S4.dettonville.int
      safe: Windows-Server-Local-Admin
      username: administrator
    - address: 172.21.33.8
      automatic_management_enabled: true
      domain_type: local
      platform_account_type: recon
      platform_id: WND-Local-Managed-DMZ
      platform_logon_domain: 172.21.33.8
      platform_notes: WINANSD1S1.dettonville.int
      safe: A-T-careconlocal
      username: careconlocal
    - address: 172.21.33.8
      automatic_management_enabled: true
      domain_type: local
      groups:
      - Administrators
      local_admin_username: administrator
      managed: true
      platform_account_type: platform
      platform_id: WND-Local-Managed-DMZ
      platform_logon_domain: 172.21.33.8
      platform_notes: WINANSD1S1.dettonville.int
      safe: Windows-Server-Local-Admin
      username: administrator
  # Produces the sorted list:
  # 
  #  my_list:
  #   - address: 172.21.33.8
  #     automatic_management_enabled: true
  #     domain_type: local
  #     groups:
  #     - Administrators
  #     local_admin_username: administrator
  #     managed: true
  #     platform_account_type: platform
  #     platform_id: WND-Local-Managed-DMZ
  #     platform_logon_domain: 172.21.33.8
  #     platform_notes: WINANSD1S1.dettonville.int
  #     safe: Windows-Server-Local-Admin
  #     username: administrator
  #   - address: 172.21.33.8
  #     automatic_management_enabled: true
  #     domain_type: local
  #     platform_account_type: recon
  #     platform_id: WND-Local-Managed-DMZ
  #     platform_logon_domain: 172.21.33.8
  #     platform_notes: WINANSD1S1.dettonville.int
  #     safe: A-T-careconlocal
  #     username: careconlocal
  #   - address: 172.31.25.54
  #     automatic_management_enabled: true
  #     domain_type: local
  #     groups:
  #     - Administrators
  #     local_admin_username: administrator
  #     managed: true
  #     platform_account_type: platform
  #     platform_id: WND-Local-Managed-DMZ
  #     platform_logon_domain: 172.31.25.54
  #     platform_notes: WINANSD1S4.dettonville.int
  #     safe: Windows-Server-Local-Admin
  #     username: administrator
  #   - address: 172.31.25.54
  #     automatic_management_enabled: true
  #     domain_type: local
  #     platform_account_type: recon
  #     platform_id: WND-Local-Managed-DMZ
  #     platform_logon_domain: 172.31.25.54
  #     platform_notes: WINANSD1S4.dettonville.int
  #     safe: A-T-careconlocal
  #     username: careconlocal
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
from ansible_collections.dettonville.utils.plugins.module_utils.dict_utils import (
    sort_single_key,
    sort_multi_key
)


class FilterModule(object):

    def filters(self):
        return {
            'sort_dict_list': self.sort_dict_list
        }

    def sort_dict_list(self, dict_list, sort_keys):
        if isinstance(sort_keys, list):
            return sort_multi_key(dict_list, sort_keys)
        else:
            return sort_single_key(dict_list, sort_keys)
