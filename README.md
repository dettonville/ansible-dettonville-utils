
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](LICENSE)

# Dettonville Ansible Utilities Collection

The Ansible ``dettonville.utils`` collection includes plugins/filters that aid management, manipulation and visibility of data for Ansible playbooks.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.10**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## Included content

<!--start collection content-->
### Filter plugins
Name | Description
--- | ---
[dettonville.utils.sort_dict_list](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.sort_dict_list.md)|Parse cli output or text using a variety of parsers

### Lookup plugins
Name | Description
--- | ---

### Modules
Name | Description
--- | ---
[dettonville.utils.git_pacp](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.git_pacp.md)|Perform git operations including: 'clone', 'pull', 'acp', and 'pacp' (pull, add, commit and push).
[dettonville.utils.export_dicts](https://github.com/dettonville/ansible-dettonville-utils/blob/main/docs/dettonville.utils.export_dicts.md)|Write a list of flat dictionaries to a file with either csv or markdown format.

### Test plugins
Name | Description
--- | ---

<!--end collection content-->

## Installing this collection

You can install the ``dettonville.utils`` collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install dettonville.utils

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: dettonville.utils
```
## Using this collection

The most common use case for this collection is when you want to work with the complex data structures present in an Ansible playbook, inventory, or returned from modules. See each plugin documentation page for detailed examples for how these utilities can be used in tasks.


**NOTE**: For Ansible 2.9, you may not see deprecation warnings when you run your playbooks with this collection. Use this documentation to track when a module is deprecated.

### See Also:

* [Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) in the Ansible documentation for more details.

## Contributing to this collection

This collection is intended for plugins that are not platform or discipline specific. Simple plugin examples should be generic in nature. More complex examples can include real world platform modules to demonstrate the utility of the plugin in a playbook.

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR against the [dettonville.utils collection repository](https://github.com/ansible-collections/dettonville.utils). See [Contributing to Ansible-maintained collections](https://docs.ansible.com/ansible/devel/community/contributing_maintained_collections.html#contributing-maintained-collections) for complete details.

See the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html) for details on contributing to Ansible.

### Developer notes

- 100% code coverage is the goal, although it's not always possible. Please include unit and integration tests with all PRs. PRs should not cause a decrease in code coverage.
- Filter plugins should be 1 per file, with an included DOCUMENTATION string, or reference a lookup plugin with the same name.
- Action, filter, and lookup plugins should use argspec validation. See [AnsibleArgSpecValidator](https://github.com/dettonville/ansible-dettonville-utils/blob/main/plugins/module_utils/common/argspec_validate.py).
- This collection should not depend on other collections for imported code
- Use of the latest version of black is required for formatting (black -l79)
- The README contains a table of plugins. Use the [collection_prep](https://github.com/ansible-network/collection_prep) utilities to maintain this.


### Code of Conduct
This collection follows the Ansible project's
[Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html).
Please read and familiarize yourself with this document.


## Release notes
<!--Add a link to a changelog.md file or an external docsite to cover this information. -->
Release notes are available [here](https://github.com/dettonville/ansible-dettonville-utils/blob/main/changelogs/CHANGELOG.rst)
For automated release announcements refer [here](https://twitter.com/AnsibleContent).


## Roadmap
For information on releasing, versioning and deprecation see the [stratergy document](https://access.redhat.com/articles/4993781).

In general, major versions can contain breaking changes, while minor versions only contain new features (like new plugin addition) and bugfixes.
The releases will be done on an as-needed basis when new features and/or bugfixes are done.

<!-- Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle. -->

## More information

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)
