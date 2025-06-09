#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Lee Johnson (ljohnson@dettonville.com)
# Apache License v2.0


from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: export_dicts
author:
    - "Lee Johnson (@lj020326)"
short_description: Write a list of flat dictionaries to a file with either csv or markdown format.
description:
    - Write a list of flat dictionaries (a dictionary mapping fieldnames to strings or numbers) to a flat file using a
      specified format choice (csv or markdown) from a list of provided column names, headers and column list order.
options:
    file:
        required: true
        type: path
        description:
            - File path where file will be written/saved.
    format:
        description:
          - C(csv) write to csv formatted file.
            C(md)  write to markdown formatted file.
            If the 'format' is not specified, it will be derived from the file extension (e.g., *.md, *.csv).
        required: false
        type: str
        choices: [ csv, md ]
        default: "csv"
    export_list:
        aliases: ['list']
        required: true
        type: list
        elements: dict
        description:
            - Specifies a list of dicts to write to flat file.
    column_list:
        aliases: ['columns']
        description:
            - List of column dictionary specifications for each column in the file.  
              Each column element should contain a dict specifying values for the 'name' and 'header' keys.
              If the 'column_list' is not specified, it will be derived from the keys of the first row in the
              export_list.
        required: false
        default: []
        type: list
        elements: dict

'''  # NOQA

EXAMPLES = r'''
- name: csv | Write file1.csv
  export_dicts:
    file: /tmp/test-exports/file1.csv
    format: csv
    export_list: 
      - { key1: "value11", key2: "value12", key3: "value13", key4: "value14" }
      - { key1: "value21", key2: "value22", key3: "value23", key4: "value24" }
      - { key1: "value31", key2: "value32", key3: "value33", key4: "value34" }
      - { key1: "value41", key2: "value42", key3: "value43", key4: "value44" }

- name: md | Write markdown export_dicts.md
  export_dicts:
    file: /tmp/test-exports/export_dicts.md
    format: md
    export_list: 
      - { key1: "value11", key2: "value12", key3: "value13", key4: "value14" }
      - { key1: "value21", key2: "value22", key3: "value23", key4: "value24" }
      - { key1: "value31", key2: "value32", key3: "value33", key4: "value34" }
      - { key1: "value41", key2: "value42", key3: "value43", key4: "value44" }

- name: csv with headers | Write file1.csv
  export_dicts:
    file: /tmp/test-exports/file1.csv
    format: csv
    columns: 
      - { "name": "key1", "header": "Key #1" }
      - { "name": "key2", "header": "Key #2" }
      - { "name": "key3", "header": "Key #3" }
      - { "name": "key4", "header": "Key #4" }
    export_list: 
      - { key1: "value11", key2: "value12", key3: "value13", key4: "value14" }
      - { key1: "value21", key2: "value22", key3: "value23", key4: "value24" }
      - { key1: "value31", key2: "value32", key3: "value33", key4: "value34" }
      - { key1: "value41", key2: "value42", key3: "value43", key4: "value44" }

- name: md with headers | Write markdown export_dicts.md
  export_dicts:
    file: /tmp/test-exports/export_dicts.md
    format: md
    columns: 
      - { "name": "key1", "header": "Key #1" }
      - { "name": "key2", "header": "Key #2" }
      - { "name": "key3", "header": "Key #3" }
      - { "name": "key4", "header": "Key #4" }
    export_list: 
      - { key1: "båz", key2: "value12", key3: "value13", key4: "value14" }
      - { key1: "value21", key2: "ﬀöø", key3: "value23", key4: "value24" }
      - { key1: "value31", key2: "value32", key3: "ḃâŗ", key4: "value34" }
      - { key1: "value41", key2: "value42", key3: "ﬀöø", key4: "båz" }
'''  # NOQA

RETURN = r'''
message: 
    description: Status message for export
    type: str
    returned: always
    sample: "The markdown file has been created successfully at /foo/bar/test.md"
failed: 
    description: True if export failed
    type: bool
    returned: always
changed: 
    description: True if successful
    type: bool
    returned: always

'''  # NOQA

# noqa: E402 - ansible module imports must occur after docs
from ansible.module_utils.basic import AnsibleModule

import os
import sys
import logging
import pprint

from ansible_collections.dettonville.utils.plugins.module_utils.export_dict_utils import write_markdown_file, write_csv_file


def get_file_format(file):
    # type: (str) -> [str]
    format = 'csv'
    if "." in file:
        format = file.split('.')[-1].lower()
    return format


def main():
    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        message=''
    )

    export_result = None

    # define available arguments/parameters a user can pass to the module
    argument_spec = dict(
        file=dict(required=True, type='path'),
        format=dict(choices=['md', 'csv'], default=None),
        export_list=dict(required=True, aliases=['list'], type='list', elements='dict'),
        column_list=dict(aliases=['columns'], type='list', elements='dict'),
        logging_level=dict(type='str', choices=["NOTSET", "DEBUG", "INFO", "ERROR"], default="INFO"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    loglevel = module.params.get('logging_level')
    logging.basicConfig(
        level=loglevel
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    file = module.params.get('file')

    destination_path = os.path.dirname(file)
    if not os.path.exists(destination_path):
        module.fail_json(rc=257, msg='Destination directory %s does not exist!' % destination_path)

    # file_format = module.params.get('format', get_file_format(file))
    file_format = module.params.get('format') or get_file_format(file)
    column_list = module.params.get('column_list') or []
    export_list = module.params.get('export_list')

    logging.info("file_format => %s" % file_format)
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

    logging.info("column_list => %s" % pprint.pformat(column_list))

    for column in column_list:
        column_name = column['name']
        if not column_name:
            module.fail_json(msg='Column name not found', **result)

    if file_format == "md":
        export_result = write_markdown_file(module, file, export_list, column_list)
    elif file_format == "csv":
        export_result = write_csv_file(module, file, export_list, column_list)

    # print('export_result: %s' % export_result)

    result['changed'] = export_result['changed']
    result['message'] = export_result['message']

    # print('result: %s' % result)
    logging.info("result => %s" % pprint.pformat(result))
    module.exit_json(**result)


if __name__ == "__main__":
    main()
