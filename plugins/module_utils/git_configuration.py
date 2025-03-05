from __future__ import absolute_import, division, print_function
__metaclass__ = type


class GitConfiguration:

    def __init__(self, module):
        self.module = module
        self.repo_dir = self.module.params.get('path')
        self.git_bin_path = self.module.params.get('executable') or self.module.get_bin_path('git', True)

    def user_config(self, user_config=None):
        """
        Config git local user.name and user.email.

        args:
            * module:
                type: dict()
                descrition: Ansible basic module utilities and module arguments.
        return:
            * result:
                type: dict()
                description: updated changed status.
        """
        PARAMETERS = ['name', 'email']
        result = dict()

        for parameter in PARAMETERS:
            if user_config[parameter]:
                config_parameter = user_config[parameter]
            else:
                config_parameter = self.module.params.get('user_{0}'.format(parameter))

            if config_parameter:
                command = [self.git_bin_path, 'config', '--local', 'user.{0}'.format(parameter)]
                _rc, output, _error = self.module.run_command(command, cwd=self.repo_dir)

                if output != config_parameter:
                    command.append(config_parameter)
                    _rc, output, _error = self.module.run_command(command, cwd=self.repo_dir)

                    result.update({parameter: output, "changed": True})

        return result
