# dettonville.utils.export_dicts

**Write a list of flat dictionaries to a file with either csv or markdown format.**

Version added: 1.0.0

-   [Synopsis](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#synopsis)
-   [Parameters](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#parameters)
-   [Notes](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#notes)
-   [Examples](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#examples)
-   [Return Values](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#return-values)
-   [Status](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#status)

## [Synopsis](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#synopsis)

- Write a list of flat dictionaries (a dictionary mapping fieldnames to strings or numbers) to a flat file using a
  specified format choice (csv or markdown) from a list of provided column names, headers and column list order.

## [Parameters](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#parameters)

| Parameter                       | Choices/Defaults | Configuration | Comments |
|---------------------------------| --- | --- | --- |
| **file** str / required         |  |  | File path where file will be written/saved.
| **format**                      | `csv`(DEFAULT) OR `md` |  | `csv` write to csv formatted file, `md` write to markdown formatted file.<br>If the 'format' is not specified, it will be derived from the file extension (e.g., *.md, *.csv).
| **export_list** list / required |  |  | Specifies a list of dicts to write to flat file.
| **column_list** list            |  |  | List of column dictionary specifications for each column in the file.


## [Examples](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#examples)

```yaml
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

- name: md with headers | Write markdown export_dicts.md with format implied by `file` extension
  export_dicts:
    file: /tmp/test-exports/export_dicts.md
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

```


## [Status](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#status)


### [Authors](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md#authors)

-   Lee Johnson (@lj020326)
