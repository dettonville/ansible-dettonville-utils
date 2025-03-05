
import os
from os.path import join, dirname, abspath

import re
from glob import glob
# import pathlib
import logging

from typing import List, Any, Tuple

import pytest

# ref: https://pytest-with-eric.com/introduction/pytest-run-single-test/
# ref: https://medium.com/swlh/build-your-first-automated-test-integration-with-pytest-jenkins-and-docker-ec738ec43955
# ref: https://www.linkedin.com/pulse/how-use-jenkins-run-automated-python-tests-antonio-quarta/

# ref: https://pypi.org/project/pytest-shell-utilities/
# ref: https://pytest-shell-utilities.readthedocs.io/en/latest/index.html
# ref: https://github.com/saltstack/pytest-shell-utilities
# ref: https://github.com/saltstack/pytest-shell-utilities/blob/main/tests/functional/shell/test_script_subprocess.py
# ref: https://github.com/saltstack/pytest-shell-utilities/blob/main/tests/unit/utils/processes/test_processresult.py

test_components = [
    'export_dicts',
    'git_pacp',
    'remove_dict_keys',
    'remove_sensitive_keys',
    'sort_dict_list'
]

log_level = "INFO"
logging.basicConfig(
    level=log_level
)


# @pytest.fixture(params=test_components)
# def test_component(request):
#     return request.param


# ref: https://docs.pytest.org/en/7.1.x/how-to/fixtures.html
@pytest.fixture
def request_path(request):
    return request.path


@pytest.fixture
def script_path(request_path):
    script_dir = dirname(request_path)
    # script_dir = os.getcwd()
    script_path = join(script_dir, "run-module-tests.sh")
    return script_path


# ref: https://stackoverflow.com/questions/63210834/run-pytest-for-each-file-in-directory
# ref: https://stackoverflow.com/questions/59309558/is-it-possible-to-use-a-fixture-inside-pytest-generate-tests
def get_test_cases() -> list[tuple[str, str]]:
    # script_dir = os.getcwd()
    script_dir = dirname(os.path.realpath(__file__))
    test_case_list: list[tuple[str | Any, Any]] = []
    for test_component in test_components:
        component_testvars_dir = join(script_dir, "test_component", "vars", test_component)
        logging.debug("component_testvars_dir=%s" % component_testvars_dir)

        test_var_files = list(glob(join(component_testvars_dir, "testdata_*.yml")))

        for filename in test_var_files:
            test_case = re.findall('testdata_(.*?).yml', str(filename))[0]
            logging.debug("test_case=%s" % test_case)
            test_input_data = (test_component, test_case)
            test_case_list.append(test_input_data)
    test_case_list.sort()
    return test_case_list


test_case_list = get_test_cases()
# logging.debug("test_case_list=%s" % test_case_list)


# # ref: https://pytest-with-eric.com/introduction/pytest-generate-tests/
# def pytest_generate_tests(metafunc):
#     if 'test_component' in metafunc.fixturenames:
#         # Generate test cases based on the test_case_list
#         metafunc.parametrize('test_component,test_case', test_case_list)


# ref: https://docs.pytest.org/en/latest/reference/reference.html#request
@pytest.mark.parametrize("test_component,test_case", test_case_list)
def test_components(shell, script_path, test_component, test_case):
    test_case_extra_vars = "--extra-vars \"test_case_id_list=[\'%s\']\"" % test_case
    test_command_list = [script_path, "-t", test_component, test_case_extra_vars]
    logging.info("test_command_list=%s" % test_command_list)
    # ref: https://stackoverflow.com/questions/7745952/how-to-expand-a-list-to-function-arguments-in-python#7745986
    ret = shell.run(*test_command_list)
    assert ret.returncode == 0
