# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
  name: remove_sensitive_keys
  short_description: Remove key(s) with specified list of regex patterns from nested dict/array
  version_added: 1.0.0
  author: Lee Johnson (@lj020326)
  description:
    - Remove key(s) with specified list of regex patterns from nested dict/array.
  positional: key_patterns
  options:
    _input:
      description: dictionary or list of dictionaries
      type: any
      elements: dictionary
      required: true
    key_patterns:
      description: List of key patterns to use to remove keys.
      type: list
      required: true
"""

EXAMPLES = """
- name: Remove sensitive keys from dictionaries
  ansible.builtin.debug:
    msg: "{{ my_dict | dettonville.utils.remove_sensitive_keys }}"
  vars:
    my_dict:
      administrator-172.21.33.8:
        address: 172.21.33.8
        automatic_management_enabled: true
        domain_type: local
        groups:
        - Administrators
        local_admin_username: administrator
        managed: true
        platform_account_type: platform
        platform_id: WND-Local-Managed-DMZ
        platform_logon_domain: 172.21.33.8
        platform_notes: WINANSD1S1.example.int
        safe: Windows-Server-Local-Admin
        username: administrator
        password: 39infsVSRk
      administrator-172.31.25.54:
        address: 172.31.25.54
        automatic_management_enabled: true
        domain_type: local
        groups:
        - Administrators
        local_admin_username: administrator
        managed: true
        platform_account_type: platform
        platform_id: WND-Local-Managed-DMZ
        platform_logon_domain: 172.31.25.54
        platform_notes: WINANSD1S4.example.int
        safe: Windows-Server-Local-Admin
        username: administrator
        password: 39infsVSRk
      careconlocal-172.21.33.8:
        address: 172.21.33.8
        automatic_management_enabled: true
        domain_type: local
        platform_account_type: recon
        platform_id: WND-Local-Managed-DMZ
        platform_logon_domain: 172.21.33.8
        platform_notes: WINANSD1S1.example.int
        safe: A-T-careconlocal
        username: careconlocal
        password: 39infsVSRk
      careconlocal-172.31.25.54:
        address: 172.31.25.54
        automatic_management_enabled: true
        domain_type: local
        platform_account_type: recon
        platform_id: WND-Local-Managed-DMZ
        platform_logon_domain: 172.31.25.54
        platform_notes: WINANSD1S4.example.int
        safe: A-T-careconlocal
        username: careconlocal
        password: 39infsVSRk
  # Produces the dict:
  # 
  #  my_dict:
  #    administrator-172.21.33.8:
  #      address: 172.21.33.8
  #      automatic_management_enabled: true
  #      domain_type: local
  #      groups:
  #      - Administrators
  #      local_admin_username: administrator
  #      managed: true
  #      platform_account_type: platform
  #      platform_id: WND-Local-Managed-DMZ
  #      platform_logon_domain: 172.21.33.8
  #      platform_notes: WINANSD1S1.example.int
  #      safe: Windows-Server-Local-Admin
  #      username: administrator
  #    administrator-172.31.25.54:
  #      address: 172.31.25.54
  #      automatic_management_enabled: true
  #      domain_type: local
  #      groups:
  #      - Administrators
  #      local_admin_username: administrator
  #      managed: true
  #      platform_account_type: platform
  #      platform_id: WND-Local-Managed-DMZ
  #      platform_logon_domain: 172.31.25.54
  #      platform_notes: WINANSD1S4.example.int
  #      safe: Windows-Server-Local-Admin
  #      username: administrator
  #    careconlocal-172.21.33.8:
  #      address: 172.21.33.8
  #      automatic_management_enabled: true
  #      domain_type: local
  #      platform_account_type: recon
  #      platform_id: WND-Local-Managed-DMZ
  #      platform_logon_domain: 172.21.33.8
  #      platform_notes: WINANSD1S1.example.int
  #      safe: A-T-careconlocal
  #      username: careconlocal
  #    careconlocal-172.31.25.54:
  #      address: 172.31.25.54
  #      automatic_management_enabled: true
  #      domain_type: local
  #      platform_account_type: recon
  #      platform_id: WND-Local-Managed-DMZ
  #      platform_logon_domain: 172.31.25.54
  #      platform_notes: WINANSD1S4.example.int
  #      safe: A-T-careconlocal
  #      username: careconlocal

- name: Remove sensitive keys from list of dictionaries
  ansible.builtin.debug:
    msg: "{{ my_list | dettonville.utils.remove_sensitive_keys }}"
  vars:
    my_list:
    - address: 172.31.25.54
      automatic_management_enabled: true
      domain_type: local
      platform_account_type: recon
      platform_id: WND-Local-Managed-DMZ
      platform_logon_domain: 172.31.25.54
      platform_notes: WINANSD1S4.example.int
      safe: A-T-careconlocal
      username: careconlocal
      password: 39infsVSRk
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
      platform_notes: WINANSD1S4.example.int
      safe: Windows-Server-Local-Admin
      username: administrator
      password: 39infsVSRk
    - address: 172.21.33.8
      automatic_management_enabled: true
      domain_type: local
      platform_account_type: recon
      platform_id: WND-Local-Managed-DMZ
      platform_logon_domain: 172.21.33.8
      platform_notes: WINANSD1S1.example.int
      safe: A-T-careconlocal
      username: careconlocal
      password: 39infsVSRk
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
      platform_notes: WINANSD1S1.example.int
      safe: Windows-Server-Local-Admin
      username: administrator
      password: 39infsVSRk
  # Produces the list:
  # 
  #  my_list:
  #  - address: 172.31.25.54
  #    automatic_management_enabled: true
  #    domain_type: local
  #    platform_account_type: recon
  #    platform_id: WND-Local-Managed-DMZ
  #    platform_logon_domain: 172.31.25.54
  #    platform_notes: WINANSD1S4.example.int
  #    safe: A-T-careconlocal
  #    username: careconlocal
  #  - address: 172.31.25.54
  #    automatic_management_enabled: true
  #    domain_type: local
  #    groups:
  #    - Administrators
  #    local_admin_username: administrator
  #    managed: true
  #    platform_account_type: platform
  #    platform_id: WND-Local-Managed-DMZ
  #    platform_logon_domain: 172.31.25.54
  #    platform_notes: WINANSD1S4.example.int
  #    safe: Windows-Server-Local-Admin
  #    username: administrator
  #  - address: 172.21.33.8
  #    automatic_management_enabled: true
  #    domain_type: local
  #    platform_account_type: recon
  #    platform_id: WND-Local-Managed-DMZ
  #    platform_logon_domain: 172.21.33.8
  #    platform_notes: WINANSD1S1.example.int
  #    safe: A-T-careconlocal
  #    username: careconlocal
  #  - address: 172.21.33.8
  #    automatic_management_enabled: true
  #    domain_type: local
  #    groups:
  #    - Administrators
  #    local_admin_username: administrator
  #    managed: true
  #    platform_account_type: platform
  #    platform_id: WND-Local-Managed-DMZ
  #    platform_logon_domain: 172.21.33.8
  #    platform_notes: WINANSD1S1.example.int
  #    safe: Windows-Server-Local-Admin
  #    username: administrator
  #
"""

RETURN = """
  _value:
    description: A dict or list containing the results of removing the specified key patterns.
    type: any
"""

# from ansible.errors import AnsibleFilterError
# from ansible.module_utils.common._collections_compat import Mapping, Sequence
# from ansible.module_utils.six import string_types, text_type

# noinspection PyUnresolvedReferences
from ansible_collections.dettonville.utils.plugins.module_utils.dict_utils import (
    remove_keys_from_object
)

_SENSITIVE_KEYS_DEFAULT: list = [
    '(?i).*vault.*',
    '(?i).*token.*',
    '(?i).*password.*',
    '(?i).*key.*',
    '(?i).*ssh.*'
]


class FilterModule(object):
    def filters(self):
        return {"remove_sensitive_keys": self.remove_sensitive_keys}

    def remove_sensitive_keys(
        self,
        input_object: any,
        key_patterns: list = _SENSITIVE_KEYS_DEFAULT,
        additional_key_patterns: list = [],
            log_level: str = "INFO"
    ) -> any:
        # Create copy of original object to update as needed
        # ref: https://stackoverflow.com/questions/3975376/why-updating-shallow-copy-dictionary-doesnt-update-original-dictionary/3975388#3975388
        # return_obj = copy.deepcopy(input_object)

        if (additional_key_patterns):
            key_patterns.extend(additional_key_patterns)

        remove_keys_from_object(input_object, key_patterns, log_level)
        return input_object
