
# Testing Modules

## Test environment

```shell
$ export TEST_PYTHON_VERSION="3.10"
$ export ANSIBLE_KEEP_REMOTE_FILES=1
$ export ANSIBLE_DEBUG=1
$ PROJECT_DIR="$( git rev-parse --show-toplevel )"
$ COLLECTION_DIR=${PROJECT_DIR}/collections/ansible_collections/dettonville/utils
$ echo "COLLECTION_DIR=${COLLECTION_DIR}"
$ cd ${COLLECTION_DIR}
```


If running on MacOS may get the following error:
```output
 __NSCFConstantString initialize] may have been in progress in another thread when fork() was called

```

Resolved with the following setting:
```shell
## ref: https://github.com/ansible/ansible/issues/76322
## ref: https://github.com/ansible/ansible/issues/32499
$ export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

### Testing

## Sanity Testing

```shell
ansible-test sanity -v --docker --python ${TEST_PYTHON_VERSION} export_dicts

```

## Integration Testing

```shell
export ANSIBLE_KEEP_REMOTE_FILES=1
ansible-test integration -v --color --python ${TEST_PYTHON_VERSION} export_dicts
```

### Running tests in docker image environment
```shell
ansible-test integration -v --docker --python ${TEST_PYTHON_VERSION} export_dicts
```

### Generating formatted test reports

```shell
$ ansible-test integration -v --color --python ${TEST_PYTHON_VERSION} export_dicts | aha > tests/integration/test-results.export_dicts.html
## OR
$ ansible-test integration -v --color --docker --python ${TEST_PYTHON_VERSION} export_dicts | ansi2html > tests/integration/test-results.export_dicts.html

Falling back to tests in "tests/integration/targets/" because "roles/test/" was not found.
Assuming Docker is available on localhost.
Run command: docker -v
Detected "docker" container runtime version: Docker version 20.10.16, build aa7e414
Starting new "ansible-test-controller-Nl1njsLi" container.
Run command: docker image inspect quay.io/ansible/default-test-container:4.2.0
Run command: docker run --volume /sys/fs/cgroup:/sys/fs/cgroup:ro --privileged=false --security-opt seccomp=unconfined --volume /var/run/docker.sock:/var/run/docker.sock --name ansible-test-controller-Nl1njsLi -d quay.io/ansible/default-test-container:4.2.0
...


PLAY RECAP *********************************************************************
testhost                   : ok=101  changed=19   unreachable=0    failed=0    skipped=9    rescued=0    ignored=4   

Run command: docker exec -i ansible-test-controller-Nl1njsLi sh -c 'tar cf - -C /root/ansible_collections/dettonville/inventory/tests --exclude .tmp output | gzip'
Run command: tar oxzf - -C /Users/ljohnson/repos/silex/dettonville/dcc_common/collections/ansible_collections/dettonville/utils/tests
Run command: docker rm -f ansible-test-controller-Nl1njsLi

```

## Module export_dicts

Module integration test

```shell
ansible-test integration -v --docker --color --python ${TEST_PYTHON_VERSION} export_dicts | ansi2html > tests/integration/test-results.export_dicts.html
## OR
ansible-test integration -v --docker --color --python ${TEST_PYTHON_VERSION} export_dicts | aha > tests/integration/test-results.export_dicts.html

Falling back to tests in "tests/integration/targets/" because "roles/test/" was not found.
Assuming Docker is available on localhost.
Run command: docker -v
Detected "docker" container runtime version: Docker version 20.10.16, build aa7e414
Starting new "ansible-test-controller-Nl1njsLi" container.
Run command: docker image inspect quay.io/ansible/default-test-container:4.2.0
Run command: docker run --volume /sys/fs/cgroup:/sys/fs/cgroup:ro --privileged=false --security-opt seccomp=unconfined --volume /var/run/docker.sock:/var/run/docker.sock --name ansible-test-controller-Nl1njsLi -d quay.io/ansible/default-test-container:4.2.0
...


PLAY RECAP *********************************************************************
testhost                   : ok=101  changed=19   unreachable=0    failed=0    skipped=9    rescued=0    ignored=4   

Run command: docker exec -i ansible-test-controller-Nl1njsLi sh -c 'tar cf - -C /root/ansible_collections/dettonville/inventory/tests --exclude .tmp output | gzip'
Run command: tar oxzf - -C /Users/ljohnson/repos/silex/dettonville/dcc_common/collections/ansible_collections/dettonville/inventory/tests
Run command: docker rm -f ansible-test-controller-Nl1njsLi

```

* [Full detailed results here](./test-results.export_dicts.md)
* [Full detailed colorized results here](./test-results.export_dicts.pdf)


## Debugging modules

```shell
$ ls -Fla ../$(ls -Fla ../ | tail -16 | head -1 | cut -d':' -f2 | cut -d' ' -f2)
$ cd ${HOME}/.ansible/tmp/ansible-tmp-1657821639.432363-21127-34939542886107
./AnsiballZ_export_dicts.py explode
./AnsiballZ_export_dicts.py execute | jq
## OR if jq unavailable
./AnsiballZ_export_dicts.py execute | python -m json.tool
```

### Debugging modules on AWX control node

Log onto the tower control node 

```shell
## log into tower
## sandbox => atrsbt1s4.dettonville.org
ssh username@atrsbt1s4.dettonville.org
sudo su
```

Launch the play from AWX.

When the bubble wraps are available, save copy for debugging:
```shell
mkdir -p /tmp/save
cp -npr /tmp/bwrap_* /tmp/save/
cd /tmp/save/bwrap_35484_fq1l84h_/awx_*/project/collections/ansible_collections/dettonville/utils/tests/integration/targets
```

Run the test manually

```shell
cd /tmp/save/bwrap_35484_fq1l84h_/awx_*/project/collections/ansible_collections/dettonville/utils/tests/integration/targets
./runme.sh -vvv
```

At point of failure, run the module in debug mode
```shell
cd /var/lib/awx/.ansible/tmp
find . -type f -name *_git_pacp.py -printf "%p %TY-%Tm-%Td %TH:%TM:%TS %Tz\n"

cd /var/lib/awx/.ansible/tmp/ansible-tmp-1663850363.83-19341-84313376690859
./AnsiballZ_git_pacp.py explode
Module expanded into:
/var/lib/awx/.ansible/tmp/ansible-tmp-1663850363.83-19341-84313376690859/debug_dir

```

Save formatted args

```shell
cat debug_dir/args | python -m json.tool > debug_dir/args.json
cp -p debug_dir/args.json debug_dir/args.orig.json
cp -p debug_dir/args.json debug_dir/args
## if necessary edit any module args in debug_dir/args
```

Run the Module

```shell
export ANSIBLE_DEBUG=1
./AnsiballZ_git_pacp.py execute | python -m json.tool

```

Edit module if necessary and test

```shell
nano debug_dir/ansible_collections/dettonville/utils/plugins/module_utils/git_actions.py
./AnsiballZ_git_pacp.py execute | python -m json.tool

```

### Debugging module references

* https://docs.ansible.com/ansible/latest/dev_guide/debugging.html
* https://yaobinwen.github.io/2021/01/29/Ansible-how-to-debug-a-problematic-module.html

### Run All Tests

```shell
tests/run_tests.sh > run_test.results.txt

```
