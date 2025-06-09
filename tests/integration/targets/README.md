
# Integration Tests

## Setup development env

For local testing, make sure to set up a symbolic for the collection directory structure to be used/reference by the test runtime environment.

This can be done in the following way:

```shell
$ COLLECTION_NAMESPACE="dettonville"
$ COLLECTION_NAME="utils"
$ PROJECT_DIR="$( git rev-parse --show-toplevel )"
$ COLLECTION_SOURCE_DIR="$( basename ${PROJECT_DIR} )"
$ WORKDIR="${PROJECT_DIR}/.."
$ COLLECTION_DIR="${WORKDIR}/requirements_collections/ansible_collections/${COLLECTION_NAMESPACE}"
$ mkdir -p "${COLLECTION_DIR}"
$ cd "${COLLECTION_DIR}"
$ ln -s "../../../${COLLECTION_SOURCE_DIR}" "${COLLECTION_NAME}"
```

A bash script `setup-dev-env.sh` is available in the `${PROJECT_DIR}/${COLLECTION_NAME}/tests/integration/targets` directory to perform the same __development environment setup__ actions.

## Run Tests Locally

## Check test inventory

### Check correct hosts appear in the test groups 

```shell
ansible-inventory -i _test_inventory/ --graph --yaml testgroup_cyberark_platforms
ansible-inventory -i _test_inventory/ --graph --yaml test_cyberark_platform_lnx_managed_local_dmz
ansible-inventory -i _test_inventory/ --graph --yaml dcc_cyberark_platform_lnx_managed_local_dmz
ansible-inventory -i _test_inventory/ --graph --yaml dmz
#ansible-inventory -i _test_inventory/ --graph --yaml dettonville_utils_network_locseg_mem_dmz
```

### Check the host variable values are correctly set  

Variable value/state query based on group:

```shell
$ ansible -i _test_inventory/ -m debug -a var=group_names dmz
$ ansible -i _test_inventory/ -m debug -a var=cyberark_platform_accounts__platform_type dcc_cyberark_platform_lnx_nondomain_dmz
testd1s1.example.org | SUCCESS => {
    "cyberark_platform_accounts__platform_type": "nondomain_dmz"
}
testd2s1.example.org | SUCCESS => {
    "cyberark_platform_accounts__platform_type": "nondomain_dmz"
}

```

Query intersecting groups:
```shell
$ ansible -i _test_inventory/ -m debug -a var=group_names dmz:\&lnx_all
$ ansible -i _test_inventory/ -m debug -a var=group_names dmz:\&testgroup_lnx
$ ansible -i _test_inventory/ -m debug -a var=group_names dmz:\&testgroup_lnx:\&ntp_network
```

Query vaulted variable

```shell
$ PROJECT_DIR="$( git rev-parse --show-toplevel )"
$ cd tests
$ ansible -e @vars/vault.yml --vault-password-file ${PROJECT_DIR}/.vault_pass -i _test_inventory/ -m debug -a var=vault__ldap_readonly_password testgroup_lnx
```

```shell
$ PROJECT_DIR="$( git rev-parse --show-toplevel )"
$ cd collections/ansible_collections/dettonville/utils/tests/integration/targets
$ ansible -e @../integration_config.vault.yml --vault-password-file ${PROJECT_DIR}/.vault_pass -i _test_inventory/ -m debug -a var=ansible_user app_cdata_sync_sandbox
$ ansible -e @../integration_config.vault.yml --vault-password-file ${PROJECT_DIR}/.vault_pass -i _test_inventory/ -m debug -a var=ansible_user app_tableau
```


Query with vault and vars files variables (e.g., `./test-vars.yml`) 

```shell
$ PROJECT_DIR="$( git rev-parse --show-toplevel )"
$ cd collections/ansible_collections/dettonville/utils/tests/integration/targets
$ ansible -e @../integration_config.vault.yml -e @test-vars.yml \
    --vault-password-file \
    ${PROJECT_DIR}/.vault_pass \
    -i _test_inventory/ \
    -m debug \
    -a var=test_component_cyberark_base_url \
    localhost
$ ansible -e @test-vars.yml -e @../integration_config.vault.yml --vault-password-file ${PROJECT_DIR}/.vault_pass -i _test_inventory/ -m debug -a var=vault_platform testd1s4.example.org
$ ansible -e @test-vars.yml -e @../integration_config.vault.yml --vault-password-file ${PROJECT_DIR}/.vault_pass -i _test_inventory/ -m debug -a var=ansible_user app_cdata_sync_sandbox
$ ansible -e @test-vars.yml -e @../integration_config.vault.yml --vault-password-file ${PROJECT_DIR}/.vault_pass -i _test_inventory/ -m debug -a var=ansible_user app_tableau
```

```shell
$ PROJECT_DIR="$( git rev-parse --show-toplevel )"
$ cd tests
$ ansible -e @test-vars.yml -e @vars/vault.yml --vault-password-file ${PROJECT_DIR}/.vault_pass -i _test_inventory/ -m debug -a var=vault__ldap_readonly_password testgroup_lnx
```


```shell
$ ansible -i _test_inventory/ -m debug -a \
    var=ansible_connection,ansible_port,ansible_winrm_scheme,ansible_winrm_transport \
    dc9.example.int
$ ansible -i _test_inventory/ -m debug -a var=cyberark_platform_accounts__platform_type testgroup_cyberark_dcc_9786
winansd3s1.example.int | SUCCESS => {
    "cyberark_platform_accounts__platform_type": "managed_domain_vdi"
}
winansd3s4.example.int | SUCCESS => {
    "cyberark_platform_accounts__platform_type": "managed_domain_vdi"
}

```


### Run module tests

```shell
$ PROJECT_DIR="$( git rev-parse --show-toplevel )"
$ cd collections/ansible_collections/dettonville/utils/tests/integration/targets
## view the existing test cases
$ find -L test_component/vars/export_dicts -name "test_*.yml" | sort
$ find -L test_component/vars/sort_dict_list -name "test_*.yml" | sort
## runme.sh defaults via test-vars.yml to use vault TEST env
$ runme.sh -v -t sort_dict_list
$ runme.sh -v -t export_dicts
## OR 
$ run-module-tests.sh -v -t export_dicts
$ run-module-tests.sh -v -t sort_dict_list
```

### Run specific test case

```shell
$ run-module-tests.sh -v -t export_dicts --extra-vars \'{\"test_case_id_list\": [\"01\"]}\'
$ run-module-tests.sh -v -t sort_dict_list --extra-vars \'{\"test_case_id_list\": [\"02\"]}\'
$ run-module-tests.sh -v -t export_dicts --extra-vars \'{\"test_case_id_list\": [\"01\",\"08\"]}\'
```

### Run role test on hosts

```shell
$ run-role-tests.sh -v -t display-hostvars -l testd1s4.example.org
$ run-role-tests.sh -v -t display-dettonville-utils-vars -l testd1s4.example.org
$ run-role-tests.sh -v -t display-dettonville-utils-vars -l testgroup
$ run-role-tests.sh -v -l winansd1s1.example.int
$ run-role-tests.sh -t display-hostvars
```

#### Run specific set of test cases

```shell
$ run-module-tests.sh -v -t export_dicts --extra-vars \'{\"test_case_id_list\": [\"01\",\"02\"]}\'
```

#### Run test cases with regex pattern

The following will run all test cases with pattern test_*01*.yml.
This will effectively result in running just the first case for each test case group/category.

```shell
$ run-module-tests.sh -v -t sort_dict_list
$ run-module-tests.sh -v -t remove_dict_keys
$ run-module-tests.sh -v -t remove_sensitive_keys
$ run-module-tests.sh -v -t export_dicts
$ run-module-tests.sh -v -t export_dicts --extra-vars \'{\"test_case_id_list\": [\"10\"]}\'
$ run-module-tests.sh -v -t sort_dict_list --extra-vars \'{\"test_case_id_list\": [\"01\"]}\'
$ run-module-tests.sh -v -t remove_dict_keys --extra-vars \'{\"test_case_id_list\": [\"01\"]}\'
$ run-module-tests.sh -v -t remove_sensitive_keys --extra-vars \'{\"test_case_id_list\": [\"01\"]}\'
$ run-module-tests.sh -v -t git_pacp
## To run all module tests
$ run-module-tests.sh -v
```

### Run pytest wrapper

The pytest wrapper method uses the ['pytest-shell'](https://pytest-shell-utilities.readthedocs.io/en/latest/index.html#usage) plugin to launch the `run-module-tests.sh` script.

Using the pytest wrapper has the benefit of generating the test results in a junit format for pipeline utilization. 

```shell
## To list all the module test cases: 
$ run-pytest.sh -l

## To run all the module test cases for the `export_dicts` plugin: 
$ run-pytest.sh export_dicts

## To run the module test for the `export_dicts` plugin and for only test case '01' 
$ run-pytest.sh export_dicts-01

```

### Run role test on hosts

```shell
$ run-role-tests.sh -v -l testd1s1.example.org
$ run-role-tests.sh -v -l winansd1s1.example.int
$ run-role-tests.sh -t display-hostvars
$ run-role-tests.sh -t display-hostvars -l testd1s1.example.org
$ run-role-tests.sh -v -t display-dettonville-utils-vars -l testd1s4.example.org
```


## Debugging test module

```shell
$ cd ${HOME}/.ansible/tmp/

## find last 10 export_dicts module execs sorted order
## use gfind if using MacOS brew installed gnu utils 
$ find . -maxdepth 2 -name "*.py" -type f -printf "\n%TY-%Tm-%Td %AT %p" |sort -nk1 -nk2 | grep export_dicts | tail -10
```

### debug export_dicts
```shell
## find last export_dicts module exec
$ find .  -maxdepth 2 -name "*.py" -type f -printf "\n%TY-%Tm-%Td %AT %p" |sort -nk1 | grep export_dicts | tail -1
$ find .  -maxdepth 2 -name "*.py" -type f -printf "\n%TY-%Tm-%Td %AT %p" |sort -nk1 | grep git_pacp | tail -1
## cd into last module exec debug dir
$ cd $(dirname $(find . -maxdepth 2 -name "*.py" -type f -printf "\n%TY-%Tm-%Td %AT %p" | sort -nk1 | grep export_dicts | tail -1 | cut -d' ' -f3))
$ ./AnsiballZ_export_dicts.py explode
$ ./AnsiballZ_export_dicts.py execute | jq
## if wanting to capture the log for reference
$ ./AnsiballZ_export_dicts.py execute 2>&1 | tee test-case.log 
```

Define function to perform regular/repetitive debug tasks
E.g., in ~/.bash_functions or ~/.bashrc:
```shell
function explodeansibletest() {

  export ANSIBLE_DEBUG=1 && \
  recent=$(find . -name \*.py | head -n1) && \
  ${recent} explode && \
  cat debug_dir/args | jq > debug_dir/args.json && \
  cp debug_dir/args.json debug_dir/args && \
  cp debug_dir/args.json debug_dir/args.orig.json

}
```

Then use as follows:
```shell
## Find module used in 2nd to last step
$ ls -Fla ../$(ls -Fla ../ | tail -2 | head -1 | cut -d':' -f2 | cut -d' ' -f2)
$ cd $(ls -Fla ../ | tail -2 | head -1 | cut -d':' -f2 | cut -d' ' -f2)
$ export ANSIBLE_DEBUG=1
## perform debug_dir steps 
$ explodeansibletest
```

The function will perform the explode and json formatting:

```shell
$ export ANSIBLE_DEBUG=1
$ cd $(ls -Fla ../ | tail -2 | head -1 | cut -d':' -f2 | cut -d' ' -f2)
$ cd $(dirname $(find . -maxdepth 2 -name "*.py" -type f -printf "\n%TY-%Tm-%Td %AT %p" | sort -nk1 | grep export_dicts | tail -1 | cut -d' ' -f3))
$ explodeansibletest
$ export ANSIBLE_DEBUG=1
$ ./AnsiballZ_export_dicts.py execute
## OR
$ ./AnsiballZ_export_dicts.py execute | jq
```

### Modify code and re-run until works correctly

```shell
$ cd ~/.ansible/tmp
## NOTE:
## below navigate to the 2nd to last instance of invocation since the module is ALSO invoked/used 
## by the test harness itself for storing/logging the test results
$ cd $(dirname $(find . -maxdepth 2 -name "*.py" -type f -printf "\n%TY-%Tm-%Td %AT %p" | sort -nk1 | grep test_results_logger.py | tail -2 | head -1 | cut -d' ' -f3))
$ code .
$ ./AnsiballZ_test_results_logger.py execute
```

### Debugging integration test results

```shell
$ cd ${HOME}/.ansible/tmp
$ cd ansible-tmp-1657821639.432363-21127-34939542886107
$ ./AnsiballZ_export_dicts.py explode
Module expanded into:
...
$ ./AnsiballZ_export_dicts.py execute | jq
INFO:root:Starting Module
...

```
