from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import tempfile
import traceback

import yaml

try:
    from module_utils.messages import FailingMessage
except ImportError:
    try:
        from ansible.module_utils.messages import FailingMessage
    except ImportError:
        from ansible_collections.dettonville.utils.plugins.module_utils.messages import FailingMessage

try:
    from module_utils.six import b
except ImportError:
    from ansible.module_utils.six import b

try:
    from module_utils._text import to_native, to_text
except ImportError:
    from ansible.module_utils._text import to_native, to_text


class InventoryRepoPyYaml:

    def __init__(self, module, inventory_file_path):
        self.module = module
        self.inventory_file_path = inventory_file_path

        destination_path = os.path.dirname(self.inventory_file_path)
        if not os.path.exists(destination_path):
            self.module.fail_json(rc=257, msg='Destination directory %s does not exist!' % destination_path)

    def update_hosts(self, host_list, state='merge', backup=False):
        backup_file = None
        if not self.module.check_mode:

            # ref: https://yaml.readthedocs.io/en/latest/api.html#loading
            # ref: https://github.com/yaml/pyyaml/issues/199
            # yaml = YAML()
            yaml.preserve_quotes = True

            # filepath = Path(self.inventory_file_path)
            # data = yaml.load(filepath)

            with open(self.inventory_file_path) as file:
                try:
                    data = yaml.full_load(file)
                except AttributeError:
                    ## ref: https://stackoverflow.com/questions/55551191/module-yaml-has-no-attribute-fullloader
                    data = yaml.safe_load(file)

            # yaml.dump(data, sys.stdout)

            inventory = data['all']

            for host in host_list:
                if state in ['merge', 'overwrite']:
                    self.update_host(inventory, host, state)
                if state == 'absent':
                    self.remove_host(inventory, host)

            # ref: https://yaml.readthedocs.io/en/latest/example.html
            # ref: https://yaml.readthedocs.io/en/latest/detail.html
            # mapping = 2
            # sequence = 2
            # offset = 0
            # yaml.indent(mapping=mapping, sequence=sequence, offset=offset)

            # ref: https://pyyaml.org/wiki/PyYAMLDocumentation#events
            yaml_dumper = yaml.Dumper
            indent = 2

            # ref: https://stackoverflow.com/questions/44313992/how-to-keep-null-value-in-yaml-file-while-dumping-though-ruamel-yaml # noqa: E501 url size exceeds 120
            def my_represent_none(self, data):
                return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')

            # ref: https://stackoverflow.com/questions/44313992/how-to-keep-null-value-in-yaml-file-while-dumping-though-ruamel-yaml # noqa: E501 url size exceeds 120
            # yaml.representer.add_representer(type(None), my_represent_none)

            yaml_dumper.add_representer(type(None), my_represent_none)

            if backup:
                backup_file = self.module.backup_local(self.inventory_file_path)
                self.module.debug("backup_file={0}".format(backup_file))

            dummy, tmpfile = tempfile.mkstemp()
            self.module.debug("tmpfile={0}".format(tmpfile))

            try:
                os.remove(tmpfile)
                with open(tmpfile, 'w') as fd:
                    yaml.dump(data, fd, Dumper=yaml_dumper, indent=indent)
            except IOError:
                self.module.fail_json(msg="Unable to create temporary file %s", traceback=traceback.format_exc())

            try:
                self.module.atomic_move(tmpfile, self.inventory_file_path)
            except IOError:
                self.module.ansible.fail_json(msg='Unable to move temporary \
                                       file %s to %s, IOError' % (tmpfile, self.inventory_file_path),
                                              traceback=traceback.format_exc())
            finally:
                if os.path.exists(tmpfile):
                    os.remove(tmpfile)

        result = dict(
            changed=True,
            backup_file=backup_file,
            message="The inventory file has been updated successfully at {0}".format(self.inventory_file_path)
        )

        return result

    @staticmethod
    def update_host(inventory, host, state):

        inventory_hosts = inventory['hosts']
        inventory_groups = inventory['children']

        if 'hostvars' in host:
            hostvars = host['hostvars']
        else:
            hostvars = {}

        if host['hostname'] in inventory_hosts and state == 'merge':
            # ref: https://favtutor.com/blogs/merge-dictionaries-python
            inventory_hosts[host['hostname']].update(hostvars)
        else:
            inventory_hosts[host['hostname']] = hostvars

        if 'groups' in host:
            host_groups = host['groups']
            for group in host_groups:
                if group not in inventory_groups:
                    inventory_groups[group] = {}

                if 'hosts' not in inventory_groups[group]:
                    inventory_groups[group]['hosts'] = {}

                inventory_groups[group]['hosts'][host['hostname']] = {}

    @staticmethod
    def remove_host(inventory, host):

        inventory_hosts = inventory['hosts']
        inventory_groups = inventory['children']

        if host['hostname'] in inventory_hosts:
            inventory_hosts.pop(host['hostname'])

        for group in inventory_groups:
            if 'hosts' in inventory_groups[group]:
                group_hosts = inventory_groups[group]['hosts']

                if host['hostname'] in group_hosts:
                    group_hosts.pop(host['hostname'])


