# dettonville.utils.sort_dict_list

**Sort list of dictionaries by specified key(s).**

Version added: 1.0.0

-   [Synopsis](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#synopsis)
-   [Parameters](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#parameters)
-   [Notes](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#notes)
-   [Examples](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#examples)
-   [Return Values](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#return-values)
-   [Status](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#status)

## [Synopsis](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#synopsis)

-   Validate _data_ with provided _criteria_ based on the validation _engine_.
-   Using the parameters below- `data|dettonville.utils.sort_dict_list(sort_keys)`

## [Parameters](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#parameters)

| Parameter | Choices/Defaults | Configuration | Comments |
| --- | --- | --- | --- |
| **data** raw / required |  |  | The list of dictionaries to be sorted.
| **sort_keys** raw / required |  |  | The list of sort keys used to sort the list of dictionaries.


## [Examples](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#examples)

```yaml
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
    - address: 10.3.25.54
      automatic_management_enabled: true
      domain_type: local
      platform_account_type: recon
      platform_id: WND-Local-Managed-DMZ
      platform_logon_domain: 10.3.25.54
      platform_notes: testd1s4.example.int
      safe: A-T-careconlocal
      username: careconlocal
    - address: 10.3.25.54
      automatic_management_enabled: true
      domain_type: local
      groups:
      - Administrators
      local_admin_username: administrator
      managed: true
      platform_account_type: platform
      platform_id: WND-Local-Managed-DMZ
      platform_logon_domain: 10.3.25.54
      platform_notes: testd1s4.example.int
      safe: Windows-Server-Local-Admin
      username: administrator
    - address: 10.2.33.8
      automatic_management_enabled: true
      domain_type: local
      platform_account_type: recon
      platform_id: WND-Local-Managed-DMZ
      platform_logon_domain: 10.2.33.8
      platform_notes: testd1s1.example.int
      safe: A-T-careconlocal
      username: careconlocal
    - address: 10.2.33.8
      automatic_management_enabled: true
      domain_type: local
      groups:
      - Administrators
      local_admin_username: administrator
      managed: true
      platform_account_type: platform
      platform_id: WND-Local-Managed-DMZ
      platform_logon_domain: 10.2.33.8
      platform_notes: testd1s1.example.int
      safe: Windows-Server-Local-Admin
      username: administrator
  # Produces the sorted list:
  # 
  #  my_list:
  #   - address: 10.2.33.8
  #     automatic_management_enabled: true
  #     domain_type: local
  #     groups:
  #     - Administrators
  #     local_admin_username: administrator
  #     managed: true
  #     platform_account_type: platform
  #     platform_id: WND-Local-Managed-DMZ
  #     platform_logon_domain: 10.2.33.8
  #     platform_notes: testd1s1.example.int
  #     safe: Windows-Server-Local-Admin
  #     username: administrator
  #   - address: 10.2.33.8
  #     automatic_management_enabled: true
  #     domain_type: local
  #     platform_account_type: recon
  #     platform_id: WND-Local-Managed-DMZ
  #     platform_logon_domain: 10.2.33.8
  #     platform_notes: testd1s1.example.int
  #     safe: A-T-careconlocal
  #     username: careconlocal
  #   - address: 10.3.25.54
  #     automatic_management_enabled: true
  #     domain_type: local
  #     groups:
  #     - Administrators
  #     local_admin_username: administrator
  #     managed: true
  #     platform_account_type: platform
  #     platform_id: WND-Local-Managed-DMZ
  #     platform_logon_domain: 10.3.25.54
  #     platform_notes: testd1s4.example.int
  #     safe: Windows-Server-Local-Admin
  #     username: administrator
  #   - address: 10.3.25.54
  #     automatic_management_enabled: true
  #     domain_type: local
  #     platform_account_type: recon
  #     platform_id: WND-Local-Managed-DMZ
  #     platform_logon_domain: 10.3.25.54
  #     platform_notes: testd1s4.example.int
  #     safe: A-T-careconlocal
  #     username: careconlocal
```


## [Status](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#status)


### [Authors](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md#authors)

-   Lee Johnson (@lj020326)
